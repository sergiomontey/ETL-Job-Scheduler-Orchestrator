"""
Job Manager - Database operations for job management
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class JobManager:
    """Manages job database operations"""
    
    def __init__(self, db_path="etl_scheduler.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                job_type TEXT NOT NULL,
                command TEXT NOT NULL,
                working_directory TEXT,
                environment_vars TEXT,
                schedule_type TEXT DEFAULT 'manual',
                cron_expression TEXT,
                interval_minutes INTEGER,
                enabled BOOLEAN DEFAULT 1,
                status TEXT DEFAULT 'idle',
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                max_retries INTEGER DEFAULT 0,
                retry_delay_seconds INTEGER DEFAULT 60,
                timeout_seconds INTEGER,
                notification_email TEXT,
                notify_on_success BOOLEAN DEFAULT 0,
                notify_on_failure BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Job dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                depends_on_job_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                UNIQUE(job_id, depends_on_job_id)
            )
        ''')
        
        # Job executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT NOT NULL,
                exit_code INTEGER,
                output TEXT,
                error_output TEXT,
                retry_count INTEGER DEFAULT 0,
                triggered_by TEXT DEFAULT 'scheduler',
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_enabled ON jobs(enabled)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_job_id ON job_executions(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_status ON job_executions(status)')
        
        conn.commit()
        conn.close()
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def create_job(self, job_data):
        """Create a new job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert environment vars dict to JSON string if needed
        if 'environment_vars' in job_data and isinstance(job_data['environment_vars'], dict):
            job_data['environment_vars'] = json.dumps(job_data['environment_vars'])
        
        fields = []
        values = []
        for key, value in job_data.items():
            if key not in ['id', 'created_at', 'updated_at']:
                fields.append(key)
                values.append(value)
        
        placeholders = ','.join(['?' for _ in fields])
        field_names = ','.join(fields)
        
        query = f'INSERT INTO jobs ({field_names}) VALUES ({placeholders})'
        cursor.execute(query, values)
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
        
    def update_job(self, job_id, job_data):
        """Update an existing job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert environment vars dict to JSON string if needed
        if 'environment_vars' in job_data and isinstance(job_data['environment_vars'], dict):
            job_data['environment_vars'] = json.dumps(job_data['environment_vars'])
        
        fields = []
        values = []
        for key, value in job_data.items():
            if key not in ['id', 'created_at']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        values.append(job_id)
        
        query = f"UPDATE jobs SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
    def delete_job(self, job_id):
        """Delete a job and its dependencies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        
        conn.commit()
        conn.close()
        
    def get_job(self, job_id):
        """Get a job by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
        
    def get_all_jobs(self):
        """Get all jobs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs ORDER BY name')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
        
    def get_enabled_jobs(self):
        """Get all enabled jobs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE enabled = 1 ORDER BY name')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
        
    def update_job_status(self, job_id, field, value):
        """Update job status field"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'UPDATE jobs SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                      (value, job_id))
        
        conn.commit()
        conn.close()
        
    def update_job_last_run(self, job_id, timestamp=None):
        """Update job last run timestamp"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET last_run = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                      (timestamp, job_id))
        
        conn.commit()
        conn.close()
        
    def update_job_next_run(self, job_id, timestamp):
        """Update job next run timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET next_run = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                      (timestamp, job_id))
        
        conn.commit()
        conn.close()
        
    def add_job_dependency(self, job_id, depends_on_job_id):
        """Add a job dependency"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO job_dependencies (job_id, depends_on_job_id) 
                VALUES (?, ?)
            ''', (job_id, depends_on_job_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
            
    def remove_job_dependency(self, job_id, depends_on_job_id):
        """Remove a job dependency"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM job_dependencies 
            WHERE job_id = ? AND depends_on_job_id = ?
        ''', (job_id, depends_on_job_id))
        
        conn.commit()
        conn.close()
        
    def get_job_dependencies(self, job_id):
        """Get all dependencies for a job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM job_dependencies 
            WHERE job_id = ?
        ''', (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    def get_dependent_jobs(self, job_id):
        """Get all jobs that depend on this job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT j.* FROM jobs j
            JOIN job_dependencies d ON j.id = d.job_id
            WHERE d.depends_on_job_id = ?
        ''', (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    def check_dependencies_met(self, job_id):
        """Check if all dependencies for a job are met (completed successfully)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all dependencies
        cursor.execute('''
            SELECT depends_on_job_id FROM job_dependencies 
            WHERE job_id = ?
        ''', (job_id,))
        
        dependencies = cursor.fetchall()
        
        if not dependencies:
            conn.close()
            return True
            
        # Check each dependency's last execution
        for dep in dependencies:
            dep_job_id = dep[0]
            
            # Get the most recent execution of the dependency
            cursor.execute('''
                SELECT status FROM job_executions 
                WHERE job_id = ? 
                ORDER BY start_time DESC 
                LIMIT 1
            ''', (dep_job_id,))
            
            result = cursor.fetchone()
            
            # If no execution or last execution failed, dependencies not met
            if not result or result[0] != 'completed':
                conn.close()
                return False
                
        conn.close()
        return True
        
    def create_execution(self, job_id, triggered_by='scheduler'):
        """Create a new job execution record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_executions (job_id, start_time, status, triggered_by)
            VALUES (?, ?, 'running', ?)
        ''', (job_id, datetime.now().isoformat(), triggered_by))
        
        execution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return execution_id
        
    def update_execution(self, execution_id, **kwargs):
        """Update execution record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
            
        values.append(execution_id)
        
        query = f"UPDATE job_executions SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
    def get_execution(self, execution_id):
        """Get execution by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_executions WHERE id = ?', (execution_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
        
    def get_job_executions(self, job_id, limit=50):
        """Get recent executions for a job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM job_executions 
            WHERE job_id = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (job_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    def get_all_executions(self, limit=100, status_filter=None):
        """Get all executions with optional status filter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status_filter and status_filter != "All":
            cursor.execute('''
                SELECT e.*, j.name as job_name 
                FROM job_executions e
                JOIN jobs j ON e.job_id = j.id
                WHERE e.status = ?
                ORDER BY e.start_time DESC 
                LIMIT ?
            ''', (status_filter, limit))
        else:
            cursor.execute('''
                SELECT e.*, j.name as job_name 
                FROM job_executions e
                JOIN jobs j ON e.job_id = j.id
                ORDER BY e.start_time DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]