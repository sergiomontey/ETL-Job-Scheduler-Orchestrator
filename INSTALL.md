# ETL Job Scheduler & Orchestrator

## 📦 Installation Package

This package contains a complete, production-ready ETL job scheduler application.

### 🎯 Quick Start (3 Steps)

1. **Extract files** to a directory of your choice
2. **Run the application:**
   ```bash
   python3 run_scheduler.py
   ```
3. **Start scheduling jobs!**

That's it! No complex setup, no external dependencies required.

---

## 📁 Package Contents

### Core Application Files
- `etl_scheduler.py` - Main application (850 lines)
- `job_manager.py` - Database management (400 lines)
- `scheduler_engine.py` - Job execution engine (350 lines)
- `job_dialog.py` - Job editor dialog (600 lines)
- `workflow_canvas.py` - Visual workflow designer (350 lines)
- `log_viewer.py` - Log viewing dialog (150 lines)
- `settings_dialog.py` - Settings configuration (400 lines)
- `croniter.py` - Cron expression parser (150 lines)

### Launch Scripts
- `run_scheduler.py` - Recommended launch script
- `test_installation.py` - Verify installation

### Documentation
- `README_ETL.md` - Complete documentation (13KB)
- `QUICKSTART.txt` - Quick start guide (5.5KB)
- `PROJECT_SUMMARY.txt` - Project overview (10KB)

### Examples & Config
- `example_jobs.json` - Sample job definitions
- `requirements_etl.txt` - Optional dependencies

**Total Files:** 15 files, ~150KB total

---

## 🚀 Launch Options

### Option 1: Launch Script (Recommended)
```bash
python3 run_scheduler.py
```

### Option 2: Direct Launch
```bash
python3 etl_scheduler.py
```

### Option 3: Make Executable
```bash
chmod +x run_scheduler.py
./run_scheduler.py
```

---

## ✅ Verify Installation

Run the test suite to verify everything works:

```bash
python3 test_installation.py
```

Expected output:
```
✓ PASS - File Check
✓ PASS - Database
✓ PASS - Cron Parser
... (may show GUI warnings in headless environments)
```

---

## 📋 System Requirements

### Minimum Requirements
- **Python:** 3.7 or higher
- **OS:** Linux, macOS, or Windows
- **RAM:** 50MB
- **Disk:** 10MB

### Python Modules Required
All standard library modules (no pip install needed):
- `tkinter` - GUI framework (usually included)
- `sqlite3` - Database (built-in)
- `threading` - Multi-threading (built-in)
- `subprocess` - Process execution (built-in)
- `json`, `datetime`, `queue` - Standard library

---

## 🎓 Learning Path

### Step 1: Read Quick Start
```bash
cat QUICKSTART.txt
```
5-minute read with hands-on examples

### Step 2: Create First Job
1. Launch application
2. Click "➕ New"
3. Create a simple shell job
4. Run it manually

### Step 3: Import Examples
1. File → Import Jobs
2. Select `example_jobs.json`
3. Study the examples
4. Enable and customize

### Step 4: Read Full Docs
```bash
cat README_ETL.md
```
Complete feature documentation and advanced usage

---

## 🎯 Your First Job (1 Minute Tutorial)

1. **Launch:**
   ```bash
   python3 etl_scheduler.py
   ```

2. **Create job:**
   - Click "➕ New"
   - Name: "Hello World"
   - Type: Shell
   - Command: `echo "Hello from ETL Scheduler!"`
   - Click "Save"

3. **Run it:**
   - Select "Hello World" job
   - Click "▶️ Run"
   - See output in "Output Log" tab

4. **Schedule it:**
   - Edit job (double-click or Edit button)
   - Schedule Tab → Select "Interval"
   - Set to run every 5 minutes
   - Enable the job
   - Click "Save"

Done! Your job will now run automatically every 5 minutes.

---

## 📚 Key Features

✅ **GUI-Based** - Modern, intuitive interface  
✅ **Visual Workflow** - Drag-and-drop designer  
✅ **Dependencies** - Jobs wait for prerequisites  
✅ **Scheduling** - Cron expressions & intervals  
✅ **Retry Logic** - Automatic failure recovery  
✅ **Logging** - Complete execution history  
✅ **Notifications** - Email & Slack alerts  
✅ **Import/Export** - Backup configurations  

---

## 💡 Common Use Cases

### Automated Data Pipeline
```python
Job 1: Extract (runs at 2 AM)
  ↓
Job 2: Transform (depends on Job 1)
  ↓
Job 3: Load (depends on Job 2)
```

### Scheduled Backup
```bash
Job: Daily Backup
Schedule: 0 2 * * * (2 AM daily)
Command: tar -czf backup.tar.gz /data
Notifications: Email on failure
```

### Report Generation
```python
Job: Weekly Sales Report
Schedule: 0 9 * * 1 (Monday 9 AM)
Command: python3 generate_report.py
Notifications: Email on success
```

---

## 🔧 Configuration

### Email Notifications
File → Settings → Email Notifications
- Configure SMTP server
- Test connection
- Enable per-job notifications

### Scheduler Settings
File → Settings → Scheduler
- Check interval (default: 30 seconds)
- Max concurrent jobs (default: 5)

### Database
- Location: `etl_scheduler.db`
- Type: SQLite
- Auto-created on first run

---

## 📖 Cron Expression Quick Reference

```
Format: minute hour day month weekday

*/5 * * * *       Every 5 minutes
0 * * * *         Every hour
0 9 * * *         Daily at 9 AM
0 9 * * 1-5       Weekdays at 9 AM
0 0 * * 0         Weekly on Sunday
0 2 1 * *         Monthly on 1st
```

---

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.7+

# Test imports
python3 -c "import tkinter"  # Should not error

# Run test suite
python3 test_installation.py
```

### Jobs Not Running
1. Check job is enabled (✅ icon)
2. Verify schedule configuration
3. Check dependencies are met
4. Review execution logs

### GUI Not Showing
- Linux: Install `python3-tk`
  ```bash
  sudo apt-get install python3-tk
  ```
- macOS: Tkinter included with Python
- Windows: Tkinter included with Python

---

## 📦 Import Example Jobs

Get started quickly with pre-configured examples:

1. File → Import Jobs
2. Select `example_jobs.json`
3. Review imported jobs (disabled by default)
4. Enable and customize as needed

Includes:
- Python ETL example
- Daily backup
- Hourly sync
- Weekly report
- Data quality check

---

## 🔒 Security Notes

- **Local Only:** Runs on your machine only
- **User Permissions:** Jobs inherit your permissions
- **Passwords:** Settings stored in plain text
- **Scripts:** Only execute what you configure

**Recommendation:** Run in a controlled environment, use environment variables for secrets.

---

## 🚀 Advanced Features

### Environment Variables
Pass custom variables to jobs (JSON format):
```json
{
  "DATABASE_URL": "postgresql://localhost/mydb",
  "API_KEY": "secret123"
}
```

### Job Dependencies
Create complex workflows with automatic execution order based on dependencies.

### Retry Logic
Configure automatic retries for transient failures:
- Max retries: 0-10
- Retry delay: Customizable seconds

### Timeouts
Set maximum execution time to prevent hung jobs.

---

## 📊 Performance

- **Scalability:** Handles 100+ jobs efficiently
- **Memory:** ~50MB typical usage
- **Database:** SQLite (fast for small-medium workloads)
- **Concurrent Jobs:** Configurable (default: 5)

---

## 🎉 Success Stories

Perfect for:
- ✅ Small to medium teams
- ✅ Automated ETL pipelines
- ✅ Scheduled backups
- ✅ Report generation
- ✅ Data quality checks
- ✅ DevOps automation

Alternative to:
- Apache Airflow (simpler setup)
- Cron (with GUI & dependency management)
- Windows Task Scheduler (cross-platform)

---

## 📞 Getting Help

1. **Quick Start Guide:** `QUICKSTART.txt`
2. **Full Documentation:** `README_ETL.md`
3. **Project Overview:** `PROJECT_SUMMARY.txt`
4. **Test Installation:** `python3 test_installation.py`

---

## 🎯 Next Steps

After installation:

1. ✅ Run test suite to verify installation
2. ✅ Read QUICKSTART.txt (5 minutes)
3. ✅ Create your first job
4. ✅ Import example jobs
5. ✅ Configure notifications (optional)
6. ✅ Read full documentation

---

## 📜 Version & Status

- **Version:** 1.0.0
- **Status:** Production Ready ✅
- **Lines of Code:** ~3,500
- **Documentation:** Comprehensive
- **Test Coverage:** Core functionality
- **Maintenance:** Easy to extend

---

## 🎊 Ready to Start?

```bash
# Launch the application
python3 run_scheduler.py

# Or read the quick start
cat QUICKSTART.txt

# Or verify installation
python3 test_installation.py
```

**Enjoy your ETL scheduling! 🚀**

---

*Made with ❤️ using Python and Tkinter*
