# Collector Time Behavior Reference

## 🕐 Time-Sensitive Collectors

These collectors respect the time range slider in the dashboard:

### 1. **Email Collector** ✅ Time-Sensitive
- **Parameter**: `hours_back`
- **Behavior**: Only collects emails sent/received within the time window
- **Why**: Outlook stores timestamps for all emails
- **Example**: 48 hours = emails from last 2 days

### 2. **Browser Collector** ✅ Time-Sensitive
- **Parameter**: `hours_back`
- **Behavior**: Only collects browser history within the time window
- **Why**: Browser SQLite database has timestamps
- **Example**: 168 hours = browsing history from last 7 days

### 3. **Windows Event Log Collector** ✅ Time-Sensitive
- **Parameter**: `hours_back`
- **Behavior**: Only collects security events within the time window
- **Why**: Windows Event Log has precise timestamps
- **Example**: 24 hours = security events from last day

---

## 📸 Snapshot Collectors

These collectors capture the CURRENT STATE and ignore the time slider:

### 4. **System Collector** ❌ Not Time-Sensitive
- **Behavior**: Captures current login session, idle time, boot time
- **Why**: Shows current system state, not historical data
- **Always Returns**: 1 event (current session)

### 5. **Network Collector** ❌ Not Time-Sensitive
- **Behavior**: Captures currently active TCP/UDP connections
- **Why**: Shows what's connected RIGHT NOW
- **Returns**: Variable (depends on active connections)

### 6. **Process Collector** ❌ Not Time-Sensitive
- **Behavior**: Captures currently running processes
- **Why**: Shows what's running RIGHT NOW
- **Returns**: Variable (depends on running processes)

### 7. **File Collector** ❌ Not Time-Sensitive
- **Behavior**: Returns events from background file watcher
- **Why**: Real-time monitoring since dashboard started
- **Returns**: All file events since dashboard launch

---

## 📜 Historical Collectors

These collectors return COMPLETE HISTORY regardless of time:

### 8. **USB Device History Collector** ❌ Not Time-Sensitive
- **Behavior**: Returns ALL USB devices ever connected
- **Why**: Windows Registry doesn't store connection timestamps
- **Data Source**: `HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR`
- **Always Returns**: Complete device history (could be years old)

**Note**: This is actually a FEATURE, not a bug! For insider threat detection, you want to know about ALL devices that were ever connected, not just recent ones.

### 9. **Registry Collector** ❌ Not Time-Sensitive
- **Behavior**: Returns ALL persistence mechanisms currently in registry
- **Why**: Registry doesn't store when entries were created
- **Data Source**: Run keys, Services, Winlogon, etc.
- **Always Returns**: Current registry state

### 10. **Clipboard Collector** ⏱️ Duration-Based
- **Behavior**: Monitors clipboard for a fixed duration (30 seconds by default)
- **Why**: Real-time monitoring tool, not historical
- **Note**: Not integrated into dashboard (standalone tool)

### 11. **DNS Collector** ❌ Not Time-Sensitive
- **Behavior**: Returns ALL cached DNS queries from Windows DNS Client cache
- **Why**: Windows DNS cache doesn't store query timestamps
- **Data Source**: `ipconfig /displaydns`
- **Always Returns**: All cached queries (typically last few hours to days)
- **Note**: Cache is cleared on reboot or manual flush (`ipconfig /flushdns`)

---

## 📊 Summary Table

| Collector | Time-Sensitive? | What Time Controls |
|-----------|----------------|-------------------|
| Email | ✅ Yes | Sent/received date |
| Browser | ✅ Yes | Visit timestamp |
| Windows Events | ✅ Yes | Event timestamp |
| System | ❌ No | Current state only |
| Network | ❌ No | Current connections |
| Process | ❌ No | Currently running |
| File | ❌ No | Since dashboard start |
| USB History | ❌ No | Complete history |
| Registry | ❌ No | Current state |
| Clipboard | ⏱️ Duration | Monitoring duration |
| DNS | ❌ No | Cached queries |

---

## 💡 Why This Design?

### Time-Sensitive Collectors
These have historical data with timestamps stored in databases or logs:
- Email: Outlook stores sent/received dates
- Browser: SQLite history has visit timestamps
- Windows Events: Event Log has precise timestamps

### Snapshot Collectors
These capture "what's happening right now":
- System: Current user session
- Network: Active connections
- Process: Running processes
- File: Real-time monitoring

### Historical Collectors
These provide complete historical records:
- USB: All devices ever connected (critical for forensics)
- Registry: Current persistence mechanisms
- DNS: All cached queries (no timestamps in cache)

---

## 🎯 Best Practices

### For Insider Threat Detection:

1. **Email**: Use 7-30 days (168-720 hours) to catch patterns
2. **Browser**: Use 7 days (168 hours) for behavioral analysis
3. **Windows Events**: Use 24-48 hours for recent anomalies
4. **USB History**: Always returns complete history (no time needed)
5. **Registry**: Always returns current state (no time needed)

### For Real-Time Monitoring:

1. **System**: Check every few minutes for idle time changes
2. **Network**: Check every minute for new connections
3. **Process**: Check every minute for suspicious processes
4. **File**: Background watcher captures everything automatically

---

## 🔧 Technical Details

### Why USB History Doesn't Have Timestamps

The Windows Registry `USBSTOR` key stores:
- ✅ Device vendor/product/serial
- ✅ Device description
- ✅ Device type
- ❌ Connection timestamp
- ❌ Disconnection timestamp
- ❌ Last used date

To get USB connection timestamps, you would need:
- Windows Event Log (Event ID 20001, 20003) - but these are often not enabled
- USBDeview third-party tool
- Custom driver-level monitoring

For CERT r4.2 compatibility, the complete device history is what matters - knowing WHICH devices were connected, not exactly WHEN.

---

## 📝 Dashboard Behavior

When you adjust the time slider:
- ✅ Email, Browser, Event Log will show different results
- ❌ USB, Registry, System, Network, Process will show same results
- 📁 File shows events since dashboard started (independent of slider)

This is by design and matches how the data sources work!
