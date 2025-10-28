"""
Log Viewer - Dialog for viewing job execution logs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class LogViewer:
    """Dialog for viewing execution logs"""
    
    def __init__(self, parent, execution):
        self.parent = parent
        self.execution = execution
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Execution Log - ID: {execution['id']}")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup log viewer UI"""
        # Header with execution info
        header_frame = ttk.Frame(self.dialog, padding=10)
        header_frame.pack(fill=tk.X)
        
        info_text = f"""
Execution ID: {self.execution['id']}
Job ID: {self.execution['job_id']}
Status: {self.execution['status']}
Exit Code: {self.execution.get('exit_code', 'N/A')}
Retry Count: {self.execution.get('retry_count', 0)}
Triggered By: {self.execution.get('triggered_by', 'scheduler')}

Start Time: {self.format_timestamp(self.execution['start_time'])}
End Time: {self.format_timestamp(self.execution.get('end_time'))}
Duration: {self.calculate_duration()}
"""
        
        ttk.Label(header_frame, text=info_text, font=("Consolas", 9), 
                 justify=tk.LEFT).pack(anchor=tk.W)
        
        # Notebook for output and error tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Standard output tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Standard Output")
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#f5f5f5"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        output = self.execution.get('output', '')
        if output:
            self.output_text.insert(1.0, output)
        else:
            self.output_text.insert(1.0, "No output captured")
        self.output_text.config(state=tk.DISABLED)
        
        # Error output tab
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text="Error Output")
        
        self.error_text = scrolledtext.ScrolledText(
            error_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#fff5f5",
            fg="#cc0000"
        )
        self.error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        error = self.execution.get('error_output', '')
        if error:
            self.error_text.insert(1.0, error)
        else:
            self.error_text.insert(1.0, "No errors")
        self.error_text.config(state=tk.DISABLED)
        
        # Close button
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy, 
                  width=15).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Copy Output", command=self.copy_output, 
                  width=15).pack(side=tk.RIGHT, padx=5)
        
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return "N/A"
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
            
    def calculate_duration(self):
        """Calculate execution duration"""
        if not self.execution.get('end_time'):
            return "In progress"
            
        try:
            start = datetime.fromisoformat(self.execution['start_time'])
            end = datetime.fromisoformat(self.execution['end_time'])
            duration = end - start
            
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "N/A"
            
    def copy_output(self):
        """Copy output to clipboard"""
        output = self.output_text.get(1.0, tk.END)
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(output)
        
        # Show confirmation
        ttk.Label(self.dialog, text="✓ Copied to clipboard", 
                 foreground="green").pack(side=tk.BOTTOM)