# Installation & Testing Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Install pywin32 (Critical for New Collectors)

```bash
pip install pywin32

# After installation, run the post-install script
python .venv\Scripts\pywin32_postinstall.py -install
```

### 3. Optional: Install WMI (for USB device detection)

```bash
pip install WMI
```

---

## 🧪 Testing Individual Collectors

### Original Collectors (Already Working)

```bash
# System collector
python -m collectors.system_collector

# Network collector
python -m collectors.network_collector

# Process collector
python -m collectors.process_collector

# File collector
python -m collectors.file_collector

# Browser collector
python -m collectors.browser_collector
```

### New Collectors (CERT r4.2 Compatible)

```bash
# Email collector (requires Outlook installed)
python -m collectors.email_collector

# Windows Event Log collector (requires Admin for full access)
python -m collectors.windows_event_collector

# USB device history (requires Admin for full access)
python -m collectors.usb_device_collector

# Clipboard monitor (monitors for 30 seconds)
python -m collectors.clipboard_collector

# Registry persistence mechanisms (requires Admin for full access)
python -m collectors.registry_collector
```

---

## 🎨 Testing the Dashboard

```bash
# Start the dashboard
python dashboard.py

# Open browser to:
http://localhost:5000
```

The dashboard now has 10 buttons:
- 🖥️ System
- 🌐 Network
- ⚙️ Process
- 📁 File
- 🔍 Browser
- 📧 Email (NEW)
- 📋 Event Log (NEW)
- 💾 USB History (NEW)
- 🔑 Registry (NEW)
- 🚀 Collect All

---

## ⚠️ Important Notes

### Administrator Privileges

Some collectors require elevated privileges:

- **Windows Event Log**: Needs Admin for full Security log access
- **USB Device History**: Needs Admin for complete registry access
- **Registry Monitor**: Needs Admin for system-wide registry keys

To run as Administrator:
1. Right-click Command Prompt
2. Select "Run as Administrator"
3. Navigate to project directory
4. Activate venv and run collectors

### Outlook Configuration

The email collector requires:
- Microsoft Outlook installed
- At least one email account configured
- Outlook must have been opened at least once

If Outlook is not available, the collector will gracefully skip.

### Clipboard Monitoring

The clipboard collector runs for a specified duration (default 30 seconds) and monitors clipboard changes in real-time. It's designed for:
- Testing: Run manually to see what gets captured
- Production: Integrate into background monitoring service

---

## 🔍 Troubleshooting

### "win32com not found"

```bash
pip install pywin32
python .venv\Scripts\pywin32_postinstall.py -install
```

### "Access Denied" errors

Run Command Prompt as Administrator

### "Outlook not available"

Make sure Outlook is installed and configured with an email account

### "WMI not found"

```bash
pip install WMI
```

### Clipboard collector not detecting changes

Make sure you're copying text (not images or files) during the monitoring period

---

## 📊 Expected Output

### Email Collector
```json
{
  "event_type": "email_sent",
  "action": "send",
  "metadata": {
    "recipient_count": 3,
    "external_recipient_count": 1,
    "attachment_count": 2,
    "attachment_size_bytes": 1048576,
    "is_external": true
  }
}
```

### Windows Event Log
```json
{
  "event_type": "logon",
  "action": "login_failed",
  "metadata": {
    "event_id": 4625,
    "event_description": "Failed logon"
  }
}
```

### USB Device History
```json
{
  "event_type": "device_connect",
  "action": "usb_history",
  "metadata": {
    "device_vendor": "SanDisk",
    "device_product": "Cruzer Glide",
    "device_serial": "4C530001234567890123"
  }
}
```

### Clipboard Monitor
```json
{
  "event_type": "file_access",
  "action": "clipboard_copy",
  "metadata": {
    "clipboard_length": 1250,
    "clipboard_sensitivity": 2,
    "clipboard_patterns": "email,password_field"
  }
}
```

### Registry Persistence
```json
{
  "event_type": "process_start",
  "action": "registry_persistence",
  "metadata": {
    "registry_key": "HKLM_Run",
    "registry_value_name": "SecurityHealth",
    "sensitivity_level": 2
  }
}
```

---

## ✅ Verification Checklist

- [ ] All dependencies installed
- [ ] pywin32 post-install script executed
- [ ] Original 5 collectors working
- [ ] Email collector tested (or gracefully skipped if no Outlook)
- [ ] Windows Event Log collector tested
- [ ] USB device history collector tested
- [ ] Clipboard monitor tested
- [ ] Registry collector tested
- [ ] Dashboard loads and displays all 10 buttons
- [ ] "Collect All" button works

---

## 🎯 Next Steps

Once all collectors are verified:
1. Review `DATASET_COMPARISON.md` to see CERT r4.2 coverage
2. Proceed to Phase 2: MCP Tool Servers
3. Wrap collectors in MCP protocol for agent access
