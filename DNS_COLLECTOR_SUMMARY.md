# DNS Query Collector — Summary

## 🎯 Purpose

The DNS collector captures DNS queries from the Windows DNS Client cache to detect:
- Command & Control (C2) communication
- DNS tunneling (data exfiltration)
- Domain Generation Algorithms (DGA)
- Suspicious domain patterns
- Unusual TLDs and query patterns

## 📊 Dataset Compatibility

### UNSW-NB15 Network Intrusion Dataset
✅ **Service Features** — DNS queries are critical for network intrusion detection

### Detection Capabilities
- C2 domain detection (suspicious keywords)
- DNS tunneling (long domains, excessive subdomains)
- DGA patterns (high entropy, random-looking strings)
- Base64/hex encoding in domains (data exfiltration)
- Suspicious TLDs (.tk, .ml, .ga, .xyz, etc.)

## 🔍 How It Works

### Data Source
- Windows DNS Client cache (`ipconfig /displaydns`)
- Parses cached DNS queries with record types and responses

### Suspicious Domain Detection

The collector analyzes each domain for:

1. **Long domains** (>30 characters) — Often used in DNS tunneling
2. **Excessive subdomains** (>4 levels) — DNS tunneling indicator
3. **High digit ratio** (>30% numbers) — Suspicious pattern
4. **Suspicious TLDs** — Free/abused TLDs (.tk, .ml, .ga, .cf, .gq, .xyz, .top, .pw)
5. **Base64 patterns** — Data exfiltration encoding
6. **Hex patterns** — Encoded data (16+ hex chars)
7. **C2 keywords** — admin, panel, login, gate, bot, cmd, shell

### Sensitivity Levels

- **Level 3 (Critical)**: C2 keywords or base64 patterns
- **Level 2 (High)**: Suspicious TLDs or hex patterns
- **Level 1 (Medium)**: Other suspicious indicators
- **Level 0 (Low)**: Normal domains

## 📋 Event Schema

```json
{
  "event_type": "network_connection",
  "event_category": "network",
  "action": "dns_query",
  "resource": "example.com",
  "metadata": {
    "domain": "example.com",
    "dns_record_type": "A",
    "dns_response": "93.184.216.34",
    "is_suspicious": false,
    "suspicious_indicators": null,
    "sensitivity_level": 0
  }
}
```

## 🧪 Testing

### Standalone Test
```bash
python collectors/dns_collector.py
```

### Expected Output
```
=== DNS Query Collector Test ===

[dns_collector] Found 1683 DNS cache entries
[dns_collector] Processed 1683 DNS queries

✅ Collected 1683 DNS query events

1. Domain: example.com
   Type: A
   Response: 93.184.216.34

⚠️ Found 340 suspicious domains:
   - long-suspicious-domain.example.com (long_domain,excessive_subdomains)
   - admin-panel.xyz (suspicious_tld,c2_keyword)
```

## 🎯 Use Cases

### 1. C2 Detection
Identify domains with suspicious keywords (admin, panel, gate, bot, cmd)

### 2. DNS Tunneling
Detect long domains with excessive subdomains used for data exfiltration

### 3. DGA Detection
Identify randomly generated domains used by malware

### 4. Data Exfiltration
Detect base64/hex encoded data in DNS queries

### 5. Threat Intelligence
Flag domains with suspicious TLDs commonly used by attackers

## 📊 Real-World Results

From a typical Windows PC:
- **Total DNS queries**: 1,500-2,000 cached entries
- **Suspicious domains**: 300-400 (20-25%)
- **False positives**: Legitimate CDN domains with long names
- **True positives**: Advertising trackers, analytics, potential threats

## 🔗 Integration

### Dashboard
- Button: "DNS Queries" with 🌍 icon
- Description: "C2 detection, DGA"
- Endpoint: `/api/collect/dns`

### Time Behavior
- **NOT time-sensitive** — Shows all cached DNS queries
- Cache is cleared on reboot or manually with `ipconfig /flushdns`
- Typically contains last few hours to days of queries

## ⚠️ Limitations

1. **Cache-based**: Only shows cached queries, not real-time
2. **No timestamps**: Windows DNS cache doesn't store query times
3. **False positives**: Legitimate CDN domains may trigger alerts
4. **Cleared on reboot**: Cache is lost when system restarts

## 🚀 Future Enhancements

1. **Real-time monitoring**: Hook into DNS Client Event Log (Event ID 3008)
2. **Threat intelligence**: Integrate with VirusTotal/AbuseIPDB APIs
3. **Whitelist**: Filter known-good domains (Microsoft, Google, etc.)
4. **Query timestamps**: Use Event Log for accurate timing
5. **DNS over HTTPS**: Monitor DoH traffic (encrypted DNS)

## 📚 References

- Windows DNS Client cache: `ipconfig /displaydns`
- DNS record types: A (1), CNAME (5), AAAA (28), TXT (16), PTR (12)
- UNSW-NB15 dataset: Service features for network intrusion detection
- Content rephrased for compliance with licensing restrictions

---

**Status**: ✅ Implemented and tested  
**Date**: 2026-03-26  
**Collector**: #11 of 11
