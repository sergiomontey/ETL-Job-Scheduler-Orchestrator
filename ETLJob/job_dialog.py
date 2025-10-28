"""
Job Dialog - Dialog for creating and editing jobs
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json


class JobDialog:
    """Dialog for creating/editing jobs"""
    
    def __init__(self, parent, job_manager, job=None):
        self.parent = parent
        self.job_manager = job_manager
        self.job = job
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Job" if job else "New Job")
        self.dialog.geometry("700x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Load job data if editing
        if job:
            self.load_job_data()
            
    def setup_ui(self):
        """Setup dialog UI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic Info Tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        self.setup_basic_tab(basic_frame)
        
        # Execution Tab
        exec_frame = ttk.Frame(notebook)
        notebook.add(exec_frame, text="Execution")
        self.setup_execution_tab(exec_frame)
        
        # Schedule Tab
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Schedule")
        self.setup_schedule_tab(schedule_frame)
        
        # Dependencies Tab
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="Dependencies")
        self.setup_dependencies_tab(deps_frame)
        
        # Notifications Tab
        notif_frame = ttk.Frame(notebook)
        notebook.add(notif_frame, text="Notifications")
        self.setup_notifications_tab(notif_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, width=15).pack(side=tk.RIGHT)
        
        if self.job:
            ttk.Button(button_frame, text="Test Run", command=self.test_run, width=15).pack(side=tk.LEFT)
            
    def setup_basic_tab(self, parent):
        """Setup basic info tab"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(container, text="Job Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.name_var, width=50).grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        # Description
        ttk.Label(container, text="Description:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(container, height=3, width=50)
        self.description_text.grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Job Type
        ttk.Label(container, text="Job Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.job_type_var = tk.StringVar(value="python")
        type_frame = ttk.Frame(container)
        type_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="Python", variable=self.job_type_var, 
                       value="python").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Shell", variable=self.job_type_var, 
                       value="shell").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="SQL", variable=self.job_type_var, 
                       value="sql").pack(side=tk.LEFT, padx=5)
        
        # Command
        ttk.Label(container, text="Command/Script:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        command_frame = ttk.Frame(container)
        command_frame.grid(row=3, column=1, pady=5, sticky=tk.EW)
        self.command_text = tk.Text(command_frame, height=6, width=50)
        self.command_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(command_frame, text="Browse...", command=self.browse_script).pack(pady=5)
        
        # Enabled
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(container, text="Enabled", variable=self.enabled_var).grid(
            row=4, column=1, sticky=tk.W, pady=5)
        
        container.columnconfigure(1, weight=1)
        
    def setup_execution_tab(self, parent):
        """Setup execution tab"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Working Directory
        ttk.Label(container, text="Working Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        wd_frame = ttk.Frame(container)
        wd_frame.grid(row=0, column=1, pady=5, sticky=tk.EW)
        self.working_dir_var = tk.StringVar()
        ttk.Entry(wd_frame, textvariable=self.working_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(wd_frame, text="Browse...", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        
        # Environment Variables
        ttk.Label(container, text="Environment Variables:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        ttk.Label(container, text="(JSON format)", font=("Arial", 8)).grid(row=2, column=0, sticky=tk.W)
        self.env_vars_text = tk.Text(container, height=4, width=50)
        self.env_vars_text.grid(row=1, column=1, rowspan=2, pady=5, sticky=tk.EW)
        self.env_vars_text.insert(1.0, '{\n  "KEY": "value"\n}')
        
        # Timeout
        ttk.Label(container, text="Timeout (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.timeout_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Retry Configuration
        ttk.Label(container, text="Max Retries:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.max_retries_var = tk.StringVar(value="0")
        ttk.Spinbox(container, from_=0, to=10, textvariable=self.max_retries_var, width=20).grid(
            row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(container, text="Retry Delay (seconds):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.retry_delay_var = tk.StringVar(value="60")
        ttk.Entry(container, textvariable=self.retry_delay_var, width=20).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        container.columnconfigure(1, weight=1)
        
    def setup_schedule_tab(self, parent):
        """Setup schedule tab"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Schedule Type
        ttk.Label(container, text="Schedule Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.schedule_type_var = tk.StringVar(value="manual")
        
        schedule_frame = ttk.Frame(container)
        schedule_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(schedule_frame, text="Manual", variable=self.schedule_type_var, 
                       value="manual", command=self.update_schedule_ui).pack(anchor=tk.W)
        ttk.Radiobutton(schedule_frame, text="Interval", variable=self.schedule_type_var, 
                       value="interval", command=self.update_schedule_ui).pack(anchor=tk.W)
        ttk.Radiobutton(schedule_frame, text="Cron Expression", variable=self.schedule_type_var, 
                       value="cron", command=self.update_schedule_ui).pack(anchor=tk.W)
        
        # Interval configuration
        self.interval_frame = ttk.LabelFrame(container, text="Interval Configuration", padding=10)
        self.interval_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(self.interval_frame, text="Run every:").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value="60")
        ttk.Entry(self.interval_frame, textvariable=self.interval_var, width=10).pack(side=tk.LEFT)
        ttk.Label(self.interval_frame, text="minutes").pack(side=tk.LEFT, padx=5)
        
        # Cron configuration
        self.cron_frame = ttk.LabelFrame(container, text="Cron Configuration", padding=10)
        self.cron_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(self.cron_frame, text="Cron Expression:").pack(anchor=tk.W)
        self.cron_var = tk.StringVar()
        ttk.Entry(self.cron_frame, textvariable=self.cron_var, width=40).pack(fill=tk.X, pady=5)
        
        ttk.Label(self.cron_frame, text="Examples:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 5))
        examples = [
            "0 9 * * * - Daily at 9:00 AM",
            "0 */6 * * * - Every 6 hours",
            "0 0 * * 1 - Every Monday at midnight",
            "*/15 * * * * - Every 15 minutes"
        ]
        for example in examples:
            ttk.Label(self.cron_frame, text=example, font=("Arial", 8)).pack(anchor=tk.W, padx=10)
        
        self.update_schedule_ui()
        container.columnconfigure(1, weight=1)
        
    def setup_dependencies_tab(self, parent):
        """Setup dependencies tab"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="This job depends on:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        # List of available jobs
        list_frame = ttk.Frame(container)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.deps_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        self.deps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.deps_listbox.yview)
        
        # Load available jobs
        jobs = self.job_manager.get_all_jobs()
        self.available_jobs = {}
        for job in jobs:
            if not self.job or job['id'] != self.job['id']:  # Don't show self
                self.available_jobs[job['id']] = job['name']
                self.deps_listbox.insert(tk.END, job['name'])
        
        ttk.Label(container, text="Select jobs that must complete successfully before this job runs", 
                 font=("Arial", 8)).pack(anchor=tk.W, pady=5)
        
    def setup_notifications_tab(self, parent):
        """Setup notifications tab"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Email
        ttk.Label(container, text="Notification Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.notification_email_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.notification_email_var, width=40).grid(
            row=0, column=1, sticky=tk.EW, pady=5)
        
        # Notification options
        ttk.Label(container, text="Send notifications:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        self.notify_success_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(container, text="On Success", variable=self.notify_success_var).grid(
            row=2, column=1, sticky=tk.W, pady=2)
        
        self.notify_failure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(container, text="On Failure", variable=self.notify_failure_var).grid(
            row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(container, text="Note: SMTP configuration required in settings", 
                 font=("Arial", 8), foreground="gray").grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=15)
        
        container.columnconfigure(1, weight=1)
        
    def update_schedule_ui(self):
        """Update schedule UI based on selected type"""
        schedule_type = self.schedule_type_var.get()
        
        if schedule_type == "interval":
            self.interval_frame.grid()
            self.cron_frame.grid_remove()
        elif schedule_type == "cron":
            self.interval_frame.grid_remove()
            self.cron_frame.grid()
        else:
            self.interval_frame.grid_remove()
            self.cron_frame.grid_remove()
            
    def browse_script(self):
        """Browse for script file"""
        filename = filedialog.askopenfilename(
            title="Select Script",
            filetypes=[
                ("Python files", "*.py"),
                ("Shell scripts", "*.sh"),
                ("SQL files", "*.sql"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.command_text.delete(1.0, tk.END)
            self.command_text.insert(1.0, filename)
            
    def browse_directory(self):
        """Browse for working directory"""
        dirname = filedialog.askdirectory(title="Select Working Directory")
        if dirname:
            self.working_dir_var.set(dirname)
            
    def load_job_data(self):
        """Load job data into form"""
        self.name_var.set(self.job['name'])
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, self.job.get('description', ''))
        self.job_type_var.set(self.job['job_type'])
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, self.job['command'])
        self.enabled_var.set(self.job['enabled'])
        self.working_dir_var.set(self.job.get('working_directory', ''))
        
        if self.job.get('environment_vars'):
            self.env_vars_text.delete(1.0, tk.END)
            self.env_vars_text.insert(1.0, self.job['environment_vars'])
            
        self.timeout_var.set(self.job.get('timeout_seconds', ''))
        self.max_retries_var.set(str(self.job.get('max_retries', 0)))
        self.retry_delay_var.set(str(self.job.get('retry_delay_seconds', 60)))
        
        self.schedule_type_var.set(self.job.get('schedule_type', 'manual'))
        self.interval_var.set(str(self.job.get('interval_minutes', 60)))
        self.cron_var.set(self.job.get('cron_expression', ''))
        self.update_schedule_ui()
        
        self.notification_email_var.set(self.job.get('notification_email', ''))
        self.notify_success_var.set(self.job.get('notify_on_success', False))
        self.notify_failure_var.set(self.job.get('notify_on_failure', True))
        
        # Load dependencies
        dependencies = self.job_manager.get_job_dependencies(self.job['id'])
        dep_ids = [d['depends_on_job_id'] for d in dependencies]
        
        for i, (job_id, job_name) in enumerate(self.available_jobs.items()):
            if job_id in dep_ids:
                self.deps_listbox.selection_set(i)
                
    def validate(self):
        """Validate form data"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Job name is required")
            return False
            
        if not self.command_text.get(1.0, tk.END).strip():
            messagebox.showerror("Validation Error", "Command/script is required")
            return False
            
        # Validate environment variables JSON
        env_vars = self.env_vars_text.get(1.0, tk.END).strip()
        if env_vars:
            try:
                json.loads(env_vars)
            except:
                messagebox.showerror("Validation Error", "Environment variables must be valid JSON")
                return False
                
        # Validate numeric fields
        if self.timeout_var.get() and not self.timeout_var.get().isdigit():
            messagebox.showerror("Validation Error", "Timeout must be a number")
            return False
            
        if self.schedule_type_var.get() == 'interval':
            if not self.interval_var.get().isdigit():
                messagebox.showerror("Validation Error", "Interval must be a number")
                return False
                
        if self.schedule_type_var.get() == 'cron':
            if not self.cron_var.get().strip():
                messagebox.showerror("Validation Error", "Cron expression is required")
                return False
                
        return True
        
    def save(self):
        """Save job"""
        if not self.validate():
            return
            
        # Collect form data
        job_data = {
            'name': self.name_var.get().strip(),
            'description': self.description_text.get(1.0, tk.END).strip(),
            'job_type': self.job_type_var.get(),
            'command': self.command_text.get(1.0, tk.END).strip(),
            'enabled': self.enabled_var.get(),
            'working_directory': self.working_dir_var.get().strip(),
            'environment_vars': self.env_vars_text.get(1.0, tk.END).strip() or None,
            'timeout_seconds': int(self.timeout_var.get()) if self.timeout_var.get() else None,
            'max_retries': int(self.max_retries_var.get()),
            'retry_delay_seconds': int(self.retry_delay_var.get()),
            'schedule_type': self.schedule_type_var.get(),
            'interval_minutes': int(self.interval_var.get()) if self.schedule_type_var.get() == 'interval' else None,
            'cron_expression': self.cron_var.get().strip() if self.schedule_type_var.get() == 'cron' else None,
            'notification_email': self.notification_email_var.get().strip() or None,
            'notify_on_success': self.notify_success_var.get(),
            'notify_on_failure': self.notify_failure_var.get()
        }
        
        try:
            if self.job:
                # Update existing job
                self.job_manager.update_job(self.job['id'], job_data)
                job_id = self.job['id']
                
                # Update dependencies
                # First, remove all existing dependencies
                existing_deps = self.job_manager.get_job_dependencies(job_id)
                for dep in existing_deps:
                    self.job_manager.remove_job_dependency(job_id, dep['depends_on_job_id'])
            else:
                # Create new job
                job_id = self.job_manager.create_job(job_data)
                
            # Add selected dependencies
            selected_indices = self.deps_listbox.curselection()
            job_ids = list(self.available_jobs.keys())
            for idx in selected_indices:
                dep_job_id = job_ids[idx]
                self.job_manager.add_job_dependency(job_id, dep_job_id)
                
            job_data['id'] = job_id
            self.result = job_data
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save job:\n{str(e)}")
            
    def test_run(self):
        """Test run the job"""
        messagebox.showinfo("Test Run", "Test run functionality would execute the job immediately")
        
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()