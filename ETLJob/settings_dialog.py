"""
Settings Dialog - Application settings and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class SettingsDialog:
    """Dialog for application settings"""
    
    def __init__(self, parent, scheduler_engine):
        self.parent = parent
        self.scheduler_engine = scheduler_engine
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self.get_default_settings()
        
    def get_default_settings(self):
        """Get default settings"""
        return {
            'smtp': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': '',
                'password': '',
                'use_tls': True,
                'from_email': ''
            },
            'slack': {
                'webhook_url': '',
                'enabled': False
            },
            'scheduler': {
                'check_interval_seconds': 30,
                'max_concurrent_jobs': 5
            },
            'logging': {
                'log_level': 'INFO',
                'log_file': 'etl_scheduler.log',
                'max_log_size_mb': 100
            }
        }
        
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
            return False
            
    def setup_ui(self):
        """Setup settings UI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Email/SMTP Tab
        smtp_frame = ttk.Frame(notebook)
        notebook.add(smtp_frame, text="Email Notifications")
        self.setup_smtp_tab(smtp_frame)
        
        # Slack Tab
        slack_frame = ttk.Frame(notebook)
        notebook.add(slack_frame, text="Slack Notifications")
        self.setup_slack_tab(slack_frame)
        
        # Scheduler Tab
        scheduler_frame = ttk.Frame(notebook)
        notebook.add(scheduler_frame, text="Scheduler")
        self.setup_scheduler_tab(scheduler_frame)
        
        # Logging Tab
        logging_frame = ttk.Frame(notebook)
        notebook.add(logging_frame, text="Logging")
        self.setup_logging_tab(logging_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save, 
                  width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, 
                  width=15).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Test Email", command=self.test_email, 
                  width=15).pack(side=tk.LEFT)
        
    def setup_smtp_tab(self, parent):
        """Setup SMTP settings tab"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="SMTP Server Configuration", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # SMTP Host
        ttk.Label(container, text="SMTP Host:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.smtp_host_var = tk.StringVar(value=self.settings['smtp']['host'])
        ttk.Entry(container, textvariable=self.smtp_host_var, width=40).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # SMTP Port
        ttk.Label(container, text="SMTP Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.smtp_port_var = tk.StringVar(value=str(self.settings['smtp']['port']))
        ttk.Entry(container, textvariable=self.smtp_port_var, width=40).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Username
        ttk.Label(container, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.smtp_username_var = tk.StringVar(value=self.settings['smtp']['username'])
        ttk.Entry(container, textvariable=self.smtp_username_var, width=40).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Password
        ttk.Label(container, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.smtp_password_var = tk.StringVar(value=self.settings['smtp']['password'])
        ttk.Entry(container, textvariable=self.smtp_password_var, width=40, 
                 show="*").grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # From Email
        ttk.Label(container, text="From Email:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.smtp_from_var = tk.StringVar(value=self.settings['smtp']['from_email'])
        ttk.Entry(container, textvariable=self.smtp_from_var, width=40).grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Use TLS
        self.smtp_tls_var = tk.BooleanVar(value=self.settings['smtp']['use_tls'])
        ttk.Checkbutton(container, text="Use TLS/STARTTLS", 
                       variable=self.smtp_tls_var).grid(row=6, column=1, sticky=tk.W, pady=10)
        
        ttk.Label(container, text="Common SMTP Servers:", 
                 font=("Arial", 9, "bold")).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        examples = [
            "Gmail: smtp.gmail.com:587",
            "Outlook: smtp.office365.com:587",
            "Yahoo: smtp.mail.yahoo.com:587",
            "SendGrid: smtp.sendgrid.net:587"
        ]
        
        for i, example in enumerate(examples):
            ttk.Label(container, text=example, font=("Arial", 8)).grid(
                row=8+i, column=0, columnspan=2, sticky=tk.W, padx=10)
        
        container.columnconfigure(1, weight=1)
        
    def setup_slack_tab(self, parent):
        """Setup Slack settings tab"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="Slack Integration", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        # Enable Slack
        self.slack_enabled_var = tk.BooleanVar(value=self.settings['slack']['enabled'])
        ttk.Checkbutton(container, text="Enable Slack Notifications", 
                       variable=self.slack_enabled_var).pack(anchor=tk.W, pady=5)
        
        # Webhook URL
        ttk.Label(container, text="Webhook URL:").pack(anchor=tk.W, pady=(15, 5))
        self.slack_webhook_var = tk.StringVar(value=self.settings['slack']['webhook_url'])
        ttk.Entry(container, textvariable=self.slack_webhook_var).pack(fill=tk.X, pady=5)
        
        # Instructions
        instructions = """
To set up Slack notifications:

1. Go to your Slack workspace settings
2. Navigate to "Apps" → "Manage" → "Custom Integrations"
3. Select "Incoming Webhooks"
4. Click "Add to Slack" and choose a channel
5. Copy the Webhook URL and paste it above

The webhook URL should look like:
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
"""
        
        ttk.Label(container, text=instructions, font=("Arial", 9), 
                 justify=tk.LEFT, wraplength=500).pack(anchor=tk.W, pady=15)
        
    def setup_scheduler_tab(self, parent):
        """Setup scheduler settings tab"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="Scheduler Configuration", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Check interval
        ttk.Label(container, text="Check Interval (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.check_interval_var = tk.StringVar(
            value=str(self.settings['scheduler']['check_interval_seconds']))
        ttk.Spinbox(container, from_=10, to=300, textvariable=self.check_interval_var, 
                   width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(container, text="How often the scheduler checks for jobs to run", 
                 font=("Arial", 8), foreground="gray").grid(row=2, column=1, sticky=tk.W)
        
        # Max concurrent jobs
        ttk.Label(container, text="Max Concurrent Jobs:").grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        self.max_concurrent_var = tk.StringVar(
            value=str(self.settings['scheduler']['max_concurrent_jobs']))
        ttk.Spinbox(container, from_=1, to=20, textvariable=self.max_concurrent_var, 
                   width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(container, text="Maximum number of jobs that can run simultaneously", 
                 font=("Arial", 8), foreground="gray").grid(row=4, column=1, sticky=tk.W)
        
        container.columnconfigure(1, weight=1)
        
    def setup_logging_tab(self, parent):
        """Setup logging settings tab"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="Logging Configuration", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Log level
        ttk.Label(container, text="Log Level:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.log_level_var = tk.StringVar(value=self.settings['logging']['log_level'])
        log_level_combo = ttk.Combobox(container, textvariable=self.log_level_var, 
                                       values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                       state="readonly", width=18)
        log_level_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Log file
        ttk.Label(container, text="Log File:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        self.log_file_var = tk.StringVar(value=self.settings['logging']['log_file'])
        ttk.Entry(container, textvariable=self.log_file_var, width=40).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Max log size
        ttk.Label(container, text="Max Log Size (MB):").grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        self.max_log_size_var = tk.StringVar(
            value=str(self.settings['logging']['max_log_size_mb']))
        ttk.Entry(container, textvariable=self.max_log_size_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(container, text="Log files will be rotated when they reach this size", 
                 font=("Arial", 8), foreground="gray").grid(row=4, column=1, sticky=tk.W)
        
        container.columnconfigure(1, weight=1)
        
    def test_email(self):
        """Test email configuration"""
        messagebox.showinfo("Test Email", 
                          "Email test functionality would send a test email\n"
                          "to verify SMTP configuration.")
        
    def save(self):
        """Save settings"""
        # Update settings dict
        self.settings['smtp']['host'] = self.smtp_host_var.get()
        self.settings['smtp']['port'] = int(self.smtp_port_var.get()) if self.smtp_port_var.get().isdigit() else 587
        self.settings['smtp']['username'] = self.smtp_username_var.get()
        self.settings['smtp']['password'] = self.smtp_password_var.get()
        self.settings['smtp']['from_email'] = self.smtp_from_var.get()
        self.settings['smtp']['use_tls'] = self.smtp_tls_var.get()
        
        self.settings['slack']['webhook_url'] = self.slack_webhook_var.get()
        self.settings['slack']['enabled'] = self.slack_enabled_var.get()
        
        self.settings['scheduler']['check_interval_seconds'] = int(self.check_interval_var.get()) \
            if self.check_interval_var.get().isdigit() else 30
        self.settings['scheduler']['max_concurrent_jobs'] = int(self.max_concurrent_var.get()) \
            if self.max_concurrent_var.get().isdigit() else 5
        
        self.settings['logging']['log_level'] = self.log_level_var.get()
        self.settings['logging']['log_file'] = self.log_file_var.get()
        self.settings['logging']['max_log_size_mb'] = int(self.max_log_size_var.get()) \
            if self.max_log_size_var.get().isdigit() else 100
        
        if self.save_settings():
            messagebox.showinfo("Success", "Settings saved successfully!\n\n"
                              "Note: Some settings may require restarting the application.")
            self.dialog.destroy()