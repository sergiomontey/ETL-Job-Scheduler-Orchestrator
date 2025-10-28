# ETL Job Scheduler & Orchestrator

A comprehensive desktop application for scheduling and orchestrating ETL jobs with dependency management, built with Python and Tkinter.

## Features

### Core Functionality
- ✅ **GUI-based task scheduler** for Python, Shell, and SQL scripts
- ✅ **Drag-and-drop workflow builder** with visual dependency management
- ✅ **Job dependency management** - jobs wait for dependencies to complete
- ✅ **Retry logic and error handling** with configurable retry counts and delays
- ✅ **Comprehensive logging and monitoring** with execution history
- ✅ **Email/Slack notifications** for job success/failure
- ✅ **Flexible schedule management** (Manual, Cron, Interval)
- ✅ **Job history and execution logs** with detailed output capture

### Job Types Supported
- **Python**: Execute Python scripts with custom environments
- **Shell**: Run shell scripts and commands
- **SQL**: Execute SQL queries (via command-line tools)

### Scheduling Options
- **Manual**: Run jobs on-demand
- **Cron**: Schedule using cron expressions (e.g., `0 9 * * *` for daily at 9 AM)
- **Interval**: Run every N minutes

## Installation

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually included with Python)

### Setup

1. Install required dependencies:
```bash
pip install croniter --break-system-packages
```

2. Run the application:
```bash
python3 etl_scheduler.py
```

## Quick Start

### Creating Your First Job

1. **Launch the application**
   ```bash
   python3 etl_scheduler.py
   ```

2. **Click "New Job" or use File → New Job**

3. **Configure the job**:
   - **Basic Info Tab**:
     - Enter job name (e.g., "Daily Data Load")
     - Add description
     - Select job type (Python/Shell/SQL)
     - Enter command or browse for script
   
   - **Execution Tab**:
     - Set working directory
     - Add environment variables (JSON format)
     - Configure timeout
     - Set retry logic (max retries and delay)
   
   - **Schedule Tab**:
     - Choose schedule type (Manual/Interval/Cron)
     - For Interval: Set minutes between runs
     - For Cron: Enter cron expression
   
   - **Dependencies Tab**:
     - Select jobs that must complete before this job runs
   
   - **Notifications Tab**:
     - Enter email for notifications
     - Choose when to notify (success/failure)

4. **Click "Save"**

5. **The job will automatically run according to its schedule**

### Running a Job Manually

1. Select a job from the list
2. Click "Run" button or use Jobs → Run Now
3. View real-time output in the "Output Log" tab
4. Check execution history in "Recent Executions" tab

## User Interface Guide

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Jobs  View  Help                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌───────────────────────────────────┐│
│  │                 │  │  📋 Job Details                     ││
│  │  Job List       │  │  📊 Recent Executions               ││
│  │  with Search    │  │  📝 Output Log                      ││
│  │                 │  │  🔗 Dependencies                    ││
│  │  [Toolbar]      │  └───────────────────────────────────┘│
│  │  [Jobs Tree]    │                                         │
│  │                 │                                         │
│  └─────────────────┘                                         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ Status: Ready | 2025-10-27 14:30:00                         │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Designer

Access via **View → Workflow Designer**

- Visual representation of jobs and dependencies
- Drag and drop to reposition jobs
- Automatic layout based on dependency graph
- Color-coded job status:
  - 🔵 Blue: Idle
  - 🟢 Green: Completed
  - 🔴 Red: Failed
  - 🟠 Orange: Running

### Job List Columns

- **Name**: Job identifier
- **Type**: Python/Shell/SQL
- **Schedule**: Manual/Cron/Interval configuration
- **Status**: Current execution status
- **Last Run**: Timestamp of last execution
- **Next Run**: Scheduled next execution time

### Job Icons

- ✅ Enabled jobs
- ⏸️ Disabled jobs
- 🐍 Python jobs
- 💻 Shell jobs
- 📊 SQL jobs

## Configuration

### Email Notifications

Configure via **File → Settings → Email Notifications**

**Common SMTP Servers**:
- Gmail: `smtp.gmail.com:587`
- Outlook: `smtp.office365.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`

**Gmail Setup**:
1. Enable 2-factor authentication
2. Generate an "App Password"
3. Use the app password in settings

### Slack Notifications

Configure via **File → Settings → Slack Notifications**

1. Create an Incoming Webhook in your Slack workspace
2. Copy the webhook URL
3. Paste into settings and enable

### Scheduler Settings

- **Check Interval**: How often the scheduler checks for jobs (default: 30 seconds)
- **Max Concurrent Jobs**: Maximum parallel job executions (default: 5)

## Database

The application uses SQLite3 to store:
- Job definitions and configurations
- Job dependencies
- Execution history and logs
- Job schedules and status

**Database file**: `etl_scheduler.db` (created automatically)

### Database Schema

**Tables**:
- `jobs`: Job definitions and configuration
- `job_dependencies`: Dependency relationships
- `job_executions`: Execution history and logs

## Job Examples

### Example 1: Python ETL Script

```python
# daily_etl.py
import pandas as pd
from datetime import datetime

# Extract
data = pd.read_csv('source.csv')

# Transform
data['processed_date'] = datetime.now()
data = data[data['value'] > 0]

# Load
data.to_csv('output.csv', index=False)
print(f"Processed {len(data)} records")
```

**Job Configuration**:
- Type: Python
- Command: `daily_etl.py`
- Schedule: Cron `0 2 * * *` (2 AM daily)
- Retry: 3 attempts, 60 second delay

### Example 2: Shell Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz /data/important
echo "Backup completed: backup_$DATE.tar.gz"
```

**Job Configuration**:
- Type: Shell
- Command: `./backup.sh`
- Working Directory: `/home/user/scripts`
- Schedule: Cron `0 0 * * 0` (Weekly, Sunday midnight)

### Example 3: SQL Data Export

```sql
-- export_data.sql
COPY (
    SELECT * FROM sales 
    WHERE date = CURRENT_DATE - INTERVAL '1 day'
) TO '/tmp/daily_sales.csv' CSV HEADER;
```

**Job Configuration**:
- Type: SQL
- Command: `psql -U user -d database -f export_data.sql`
- Schedule: Interval (1440 minutes = daily)

## Cron Expression Examples

| Expression | Description |
|-----------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 */6 * * *` | Every 6 hours |
| `0 9 * * *` | Daily at 9:00 AM |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |

## Use Cases

### 1. Automated ETL Pipelines
- Extract data from various sources
- Transform and clean data
- Load into data warehouse
- Schedule with dependencies to ensure proper order

### 2. Scheduled Data Loads
- Regular database imports
- API data fetching
- File processing
- Data synchronization

### 3. Backup Automation
- Database backups
- File system backups
- Cloud uploads
- Retention management

### 4. Report Generation
- Daily/weekly reports
- Email distribution
- Dashboard updates
- Analytics processing

### 5. Data Quality Checks
- Validation scripts
- Anomaly detection
- Data profiling
- Alert generation

## Troubleshooting

### Jobs Not Running

1. **Check if job is enabled**: Look for ✅ icon in job list
2. **Verify schedule configuration**: Check Schedule tab in job editor
3. **Check dependencies**: Ensure dependent jobs completed successfully
4. **Review logs**: Check Recent Executions tab for errors

### Job Keeps Failing

1. **Check command syntax**: Verify the command is correct
2. **Verify file paths**: Ensure scripts and files exist
3. **Check permissions**: Make sure scripts are executable
4. **Review error output**: Double-click execution in Recent Executions
5. **Test manually**: Run the command outside the scheduler first

### Email Notifications Not Working

1. **Verify SMTP settings**: Check File → Settings → Email Notifications
2. **Test connection**: Use "Test Email" button in settings
3. **Check firewall**: Ensure SMTP port is not blocked
4. **Gmail users**: Use App Password, not regular password

## Advanced Features

### Environment Variables

Pass custom environment variables to jobs (JSON format):

```json
{
  "DATABASE_URL": "postgresql://localhost/mydb",
  "API_KEY": "secret123",
  "ENV": "production"
}
```

### Job Dependencies

Create complex workflows:
```
Job A (Extract)
    ↓
Job B (Transform) ← depends on A
    ↓
Job C (Load) ← depends on B
```

Jobs automatically wait for dependencies to complete successfully.

### Retry Logic

Configure automatic retries for transient failures:
- **Max Retries**: Number of retry attempts (0-10)
- **Retry Delay**: Seconds between attempts
- Helpful for network issues, temporary locks, etc.

### Timeouts

Set maximum execution time to prevent hung jobs:
- Specified in seconds
- Job will be terminated if timeout exceeded
- Useful for preventing resource exhaustion

## Import/Export

### Export Jobs

**File → Export Jobs**

Creates a JSON file with all job definitions:
```json
[
  {
    "name": "Daily ETL",
    "job_type": "python",
    "command": "daily_etl.py",
    "schedule_type": "cron",
    "cron_expression": "0 2 * * *",
    ...
  }
]
```

### Import Jobs

**File → Import Jobs**

- Import jobs from JSON file
- Useful for:
  - Backing up job configurations
  - Moving jobs between environments
  - Sharing job templates
  - Version control

## Architecture

### Components

1. **etl_scheduler.py**: Main application and UI
2. **job_manager.py**: Database operations
3. **scheduler_engine.py**: Job execution and scheduling
4. **job_dialog.py**: Job creation/editing UI
5. **workflow_canvas.py**: Visual workflow designer
6. **log_viewer.py**: Execution log viewer
7. **settings_dialog.py**: Application settings

### Threading Model

- **Main Thread**: UI and user interaction
- **Scheduler Thread**: Continuous job monitoring
- **Execution Threads**: Individual job executions
- Thread-safe communication via queue

## Security Considerations

- **Database**: Stored locally, not encrypted
- **Passwords**: Settings stored in plain text
- **Scripts**: Execute with user permissions
- **Recommendation**: Run in controlled environment, use environment variables for secrets

## Performance

- **Scalability**: Handles 100+ jobs efficiently
- **Concurrent Execution**: Configurable (default: 5)
- **Database**: SQLite performs well for small-medium workloads
- **Memory**: Lightweight, ~50MB typical usage

## Future Enhancements

Potential additions:
- Remote execution (SSH)
- REST API for job management
- Web-based UI option
- Docker container support
- Cloud storage integration
- Advanced scheduling (skip holidays, etc.)
- Real-time dashboards
- Job templates library

## License

This application is provided as-is for use in ETL and automation workflows.

## Support

For issues or questions:
1. Review this documentation
2. Check execution logs
3. Verify job configuration
4. Test commands manually

## Version

Version 1.0.0 - Initial Release

---

**Made with ❤️ using Python and Tkinter**
