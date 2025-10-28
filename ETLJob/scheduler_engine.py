"""
Scheduler Engine - Handles job scheduling and execution
"""

import subprocess
import threading
import time
import schedule
from datetime import datetime, timedelta
from croniter import croniter
import json
import os


class SchedulerEngine:
    """Manages job scheduling and execution"""
    
    def __init__(self, job_manager, status_callback=None):
        self.job_manager = job_manager
        self.status_callback = status_callback
        self.running = False
        self.scheduler_thread = None
        self.running_jobs = {}
        self.lock = threading.Lock()
        
    def start(self):
        """Start the scheduler"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
            
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Check all enabled jobs
                jobs = self.job_manager.get_enabled_jobs()
                
                for job in jobs:
                    # Skip if already running
                    if job['id'] in self.running_jobs:
                        continue
                        
                    # Check if job should run
                    should_run = False
                    
                    if job['schedule_type'] == 'interval' and job.get('interval_minutes'):
                        # Check interval-based scheduling
                        last_run = job.get('last_run')
                        if not last_run:
                            should_run = True
                        else:
                            try:
                                last_run_dt = datetime.fromisoformat(last_run)
                                next_run = last_run_dt + timedelta(minutes=job['interval_minutes'])
                                if datetime.now() >= next_run:
                                    should_run = True
                                else:
                                    # Update next run time if not set
                                    if not job.get('next_run'):
                                        self.job_manager.update_job_next_run(job['id'], next_run.isoformat())
                            except:
                                should_run = True
                                
                    elif job['schedule_type'] == 'cron' and job.get('cron_expression'):
                        # Check cron-based scheduling
                        try:
                            cron = croniter(job['cron_expression'], datetime.now())
                            next_run = cron.get_next(datetime)
                            
                            # Check if it's time to run (within last minute)
                            last_run = job.get('last_run')
                            if not last_run:
                                should_run = True
                            else:
                                last_run_dt = datetime.fromisoformat(last_run)
                                if next_run <= datetime.now() and (datetime.now() - last_run_dt).total_seconds() > 60:
                                    should_run = True
                                    
                            # Update next run time
                            if not should_run:
                                self.job_manager.update_job_next_run(job['id'], next_run.isoformat())
                        except Exception as e:
                            print(f"Error parsing cron expression for job {job['name']}: {e}")
                            
                    if should_run:
                        # Check dependencies before running
                        if self.job_manager.check_dependencies_met(job['id']):
                            # Run job in separate thread
                            thread = threading.Thread(
                                target=self.execute_job, 
                                args=(job['id'],), 
                                daemon=True
                            )
                            thread.start()
                        else:
                            print(f"Dependencies not met for job {job['name']}")
                            
            except Exception as e:
                print(f"Scheduler loop error: {e}")
                
            # Sleep for a bit before next check
            time.sleep(30)
            
    def execute_job(self, job_id, triggered_by='scheduler'):
        """Execute a job"""
        with self.lock:
            if job_id in self.running_jobs:
                print(f"Job {job_id} is already running")
                return
            self.running_jobs[job_id] = True
            
        try:
            job = self.job_manager.get_job(job_id)
            if not job:
                return
                
            # Create execution record
            execution_id = self.job_manager.create_execution(job_id, triggered_by)
            
            # Update job status
            self.job_manager.update_job_status(job_id, 'status', 'running')
            self.job_manager.update_job_last_run(job_id)
            
            # Notify UI
            if self.status_callback:
                self.status_callback(job_id, 'running')
            
            # Execute with retries
            retry_count = 0
            max_retries = job.get('max_retries', 0)
            success = False
            output = ""
            error_output = ""
            exit_code = None
            
            while retry_count <= max_retries and not success:
                try:
                    if retry_count > 0:
                        delay = job.get('retry_delay_seconds', 60)
                        print(f"Retrying job {job['name']} in {delay} seconds (attempt {retry_count + 1}/{max_retries + 1})")
                        time.sleep(delay)
                        
                    # Execute based on job type
                    if job['job_type'] == 'python':
                        output, error_output, exit_code = self._execute_python(job)
                    elif job['job_type'] == 'shell':
                        output, error_output, exit_code = self._execute_shell(job)
                    elif job['job_type'] == 'sql':
                        output, error_output, exit_code = self._execute_sql(job)
                    else:
                        error_output = f"Unknown job type: {job['job_type']}"
                        exit_code = 1
                        
                    if exit_code == 0:
                        success = True
                    else:
                        retry_count += 1
                        
                except Exception as e:
                    error_output = f"Execution error: {str(e)}"
                    exit_code = 1
                    retry_count += 1
                    
            # Update execution record
            end_time = datetime.now().isoformat()
            status = 'completed' if success else 'failed'
            
            self.job_manager.update_execution(
                execution_id,
                end_time=end_time,
                status=status,
                exit_code=exit_code,
                output=output,
                error_output=error_output,
                retry_count=retry_count - 1 if retry_count > 0 else 0
            )
            
            # Update job status
            self.job_manager.update_job_status(job_id, 'status', status)
            
            # Send notifications if configured
            if job.get('notification_email'):
                should_notify = (success and job.get('notify_on_success')) or \
                              (not success and job.get('notify_on_failure'))
                if should_notify:
                    self._send_notification(job, success, output, error_output)
                    
            # Notify UI
            if self.status_callback:
                combined_output = output
                if error_output:
                    combined_output += "\n\nERROR OUTPUT:\n" + error_output
                self.status_callback(job_id, status, combined_output)
                
        except Exception as e:
            print(f"Error executing job {job_id}: {e}")
        finally:
            with self.lock:
                self.running_jobs.pop(job_id, None)
                
    def _execute_python(self, job):
        """Execute a Python script"""
        # Prepare environment
        env = os.environ.copy()
        if job.get('environment_vars'):
            try:
                custom_env = json.loads(job['environment_vars'])
                env.update(custom_env)
            except:
                pass
                
        # Set working directory
        cwd = job.get('working_directory') or os.getcwd()
        
        # Get timeout
        timeout = job.get('timeout_seconds')
        
        # Execute
        command = ['python3'] + job['command'].split()
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr, process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return stdout, f"Process timed out after {timeout} seconds\n" + stderr, 1
            
    def _execute_shell(self, job):
        """Execute a shell command"""
        # Prepare environment
        env = os.environ.copy()
        if job.get('environment_vars'):
            try:
                custom_env = json.loads(job['environment_vars'])
                env.update(custom_env)
            except:
                pass
                
        # Set working directory
        cwd = job.get('working_directory') or os.getcwd()
        
        # Get timeout
        timeout = job.get('timeout_seconds')
        
        # Execute
        process = subprocess.Popen(
            job['command'],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr, process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return stdout, f"Process timed out after {timeout} seconds\n" + stderr, 1
            
    def _execute_sql(self, job):
        """Execute SQL query"""
        # This is a placeholder - actual implementation would connect to a database
        # For now, we'll just execute it as a shell command assuming it's using psql, mysql, etc.
        return self._execute_shell(job)
        
    def _send_notification(self, job, success, output, error_output):
        """Send email notification"""
        # Placeholder for email notification
        # In a real implementation, this would use smtplib to send emails
        status = "SUCCESS" if success else "FAILED"
        subject = f"Job {job['name']} {status}"
        
        body = f"""
Job: {job['name']}
Status: {status}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Output:
{output}

Error Output:
{error_output}
"""
        
        print(f"Would send email to {job['notification_email']}: {subject}")