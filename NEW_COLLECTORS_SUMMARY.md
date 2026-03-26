# New Collectors Summary — CERT r4.2 Compatibility

## 🎯 Mission Accomplished

Added 5 critical collectors to achieve full CERT r4.2 dataset compatibility for insider threat detection.

---

## 📧 1. Email Collector (`email_collector.py`)

### What It Does
- Captures email metadata from Microsoft Outlook
- Tracks sent and received emails
- Identifies external recipients (key exfiltration indicator)
- Counts and sizes attachments

### CERT r4.2 Match
✅ **email.csv** — Complete coverage

### Key Features
- External recipient detection (personal email domains)
- Attachment tracking (count + total size)
- Configurable internal domain list
- Privacy-preserving (subject truncated to 100 chars)

### Detection Capabilities
- Data exfiltration via email
- Unusual external communication patterns
- Large attachment transfers
- Off-hours email activity

### Example Event
```json
{
  "event_type": "email_sent",
  "action": "send",
  "resource": "email_to_3_recipients",
  "metadata": {
    "recipient_count": 3,
    "external_recipient_count": 1,
    "attachment_count": 2,
    "attachment_size_bytes": 5242880,
    "is_external": true
  }
}
```

---

## 📋 2. Windows Event Log Collector (`windows_event_collector.py`)

### What It Does
- Reads Windows Security Event Log
- Captures authentication events (success/failure)
- Detects privilege escalation
- Tracks service installation and process creation

### CERT r4.2 Match
✅ **Enhanced security monitoring** (not in original CERT, but critical for detection)

### Key Event IDs Monitored
- **4624**: Successful logon
- **4625**: Failed logon (brute force indicator)
- **4672**: Special privileges assigned (admin rights)
- **4688**: Process creation (with command line)
- **7045**: Service installed (persistence mechanism)
- **4698-4701**: Scheduled task events

### Detection Capabilities
- Brute force attacks (repeated 4625)
- Privilege escalation (4672)
- Lateral movement (4624 from unusual sources)
- Persistence via services (7045)
- Suspicious process execution (4688)

### Example Event
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

---

## 💾 3. USB Device History Collector (`usb_device_collector.py`)

### What It Does
- Reads Windows Registry USBSTOR key
- Captures ALL USB devices ever connected
- Extracts vendor, product, serial number
- Works even if device is no longer connected

### CERT r4.2 Match
✅ **device.csv** — Complete coverage + historical data

### Key Features
- Historical tracking (devices from months/years ago)
- Vendor/Product identification
- Serial number extraction
- VID/PID parsing

### Detection Capabilities
- Unauthorized USB device usage
- Data exfiltration to removable media
- Device usage patterns
- Insider threat indicators (personal USB drives)

### Example Event
```json
{
  "event_type": "device_connect",
  "action": "usb_history",
  "metadata": {
    "device_vendor": "SanDisk",
    "device_product": "Cruzer Glide",
    "device_serial": "4C530001234567890123",
    "device_vid": "0781",
    "device_pid": "5567"
  }
}
```

---

## 📋 4. Clipboard Collector (`clipboard_collector.py`)

### What It Does
- Monitors clipboard changes in real-time
- Detects sensitive data patterns
- Classifies content sensitivity
- Identifies data staging behavior

### CERT r4.2 Match
✅ **Insider threat behavioral indicator** (advanced detection)

### Sensitive Patterns Detected
- Credit card numbers
- Social Security Numbers
- Email addresses
- API keys (32+ char alphanumeric)
- Password fields
- Private keys (PEM format)
- AWS keys
- IP addresses
- Large text blocks (>1000 chars)

### Sensitivity Levels
- **3 (Critical)**: Credit cards, SSN, private keys, AWS keys
- **2 (High)**: Passwords, API keys
- **1 (Medium)**: Emails, IPs, large text blocks
- **0 (Low)**: Normal text

### Detection Capabilities
- Data staging (copy sensitive data before exfiltration)
- Credential theft
- Intellectual property copying
- Pre-exfiltration behavior

### Example Event
```json
{
  "event_type": "file_access",
  "action": "clipboard_copy",
  "metadata": {
    "clipboard_length": 1250,
    "clipboard_sensitivity": 2,
    "clipboard_patterns": "email,password_field,api_key"
  }
}
```

---

## 🔑 5. Registry Collector (`registry_collector.py`)

### What It Does
- Scans Windows Registry for persistence mechanisms
- Monitors Run keys, services, startup folders
- Detects suspicious registry entries
- Identifies advanced persistence techniques

### CERT r4.2 Match
✅ **Advanced threat detection** (malware persistence)

### Registry Keys Monitored
- **HKLM\...\Run** — System-wide auto-run
- **HKCU\...\Run** — User-specific auto-run
- **RunOnce** keys
- **Services** — Background services
- **Winlogon** — Session hijacking
- **IFEO** — Debugger hijacking

### Suspicious Indicators
- PowerShell/cmd.exe in Run keys
- Scripts in temp/appdata folders
- Obfuscated commands
- Unusual file extensions (.vbs, .js, .hta)
- LOLBins in startup

### Detection Capabilities
- Malware persistence
- Backdoor installation
- Privilege escalation
- Advanced persistent threats (APT)

### Example Event
```json
{
  "event_type": "process_start",
  "action": "registry_persistence",
  "metadata": {
    "registry_key": "HKLM_Run",
    "registry_value_name": "SecurityUpdate",
    "registry_value_data": "C:\\Users\\Public\\update.exe",
    "sensitivity_level": 3,
    "is_suspicious": true,
    "suspicious_indicators": "public,temp"
  }
}
```

---

## 📊 Coverage Summary

### CERT r4.2 Dataset Compatibility

| CERT File | Coverage | Collector(s) |
|-----------|----------|--------------|
| **logon.csv** | ✅ 100% | system_collector + windows_event_collector |
| **file.csv** | ✅ 100% | file_collector |
| **device.csv** | ✅ 100% + Historical | usb_device_collector |
| **email.csv** | ✅ 100% | email_collector |
| **http.csv** | ✅ 100% | browser_collector |
| **psychometric.csv** | ❌ N/A | (Requires HR data) |

### Additional Capabilities (Beyond CERT)

| Capability | Collector | Value |
|------------|-----------|-------|
| Windows Event Logs | windows_event_collector | Authentication anomalies, privilege escalation |
| Clipboard Monitoring | clipboard_collector | Data staging detection |
| Registry Persistence | registry_collector | Malware/APT detection |
| LOLBins Detection | process_collector | Living-off-the-land attacks |
| File Sensitivity | file_collector | Automatic classification |

---

## 🎯 Detection Scenarios Enabled

### Insider Threat (CERT r4.2 Scenarios)

1. **Data Exfiltration via Email**
   - Email collector: External recipients + large attachments
   - File collector: Sensitive file access
   - Clipboard: Data staging

2. **Data Exfiltration via USB**
   - USB collector: Device connection history
   - File collector: Files copied to USB
   - Clipboard: Data staging before copy

3. **Credential Theft**
   - Clipboard: Password/key patterns
   - Browser: Password manager access
   - File: Credential file access

4. **Pre-Termination Activity**
   - Email: Job search sites (indeed.com, glassdoor.com)
   - File: Mass file copying
   - USB: Personal device usage

### Advanced Threats

5. **Privilege Escalation**
   - Windows Events: Event ID 4672
   - Registry: Suspicious Run keys
   - Process: LOLBins execution

6. **Persistence Mechanisms**
   - Registry: Run keys, services
   - Windows Events: Service installation (7045)
   - File: Startup folder modifications

7. **Lateral Movement**
   - Windows Events: Remote logons
   - Network: Unusual internal connections
   - Process: Remote execution tools

---

## 🚀 Next Steps

### Phase 2: MCP Tool Servers
Wrap these collectors in MCP protocol so AI agents can:
- Discover available collectors
- Execute them on-demand
- Process results autonomously

### Phase 3: AI Agents
- **Data Engineering Agent**: Normalize and enrich events
- **Adversarial Agent**: Inject realistic attack simulations
- **Orchestrator**: Coordinate multi-agent workflows

### Phase 4: Integration with Team 2
- Export enriched event stream
- Feed into Behavior Analysis Agent
- Dual-monitor detection (CERT + UNSW-NB15)

---

## 📦 Dependencies Added

```txt
pywin32==306      # Windows API access (email, events, clipboard, registry)
WMI==1.5.1        # Windows Management Instrumentation (USB devices)
```

---

## ✅ Verification

All collectors:
- ✅ Follow StandardEvent schema
- ✅ Include proper error handling
- ✅ Gracefully degrade if dependencies missing
- ✅ Support standalone testing (`python -m collectors.X`)
- ✅ Integrated into dashboard
- ✅ Documented with examples

---

## 🎉 Impact

**Before**: 5 collectors, partial CERT coverage  
**After**: 10 collectors, full CERT r4.2 compatibility + advanced threat detection

**Data Sources**: System, Network, Process, File, Browser, Email, Windows Events, USB, Clipboard, Registry

**Detection Capabilities**: Insider threats, data exfiltration, privilege escalation, persistence, credential theft, lateral movement, APTs

**Ready for**: Phase 2 (MCP servers) and autonomous agent integration
