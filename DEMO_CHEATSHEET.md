# 🎯 Demo Cheatsheet - Quick Reference

**For demonstrating to your professor**

---

## 🚀 One-Command Demo

```bash
python test_mcp_full_workflow.py
```

**This single command demonstrates everything:**
- ✓ Collects real system events
- ✓ Stores events in database
- ✓ Injects CERT attack patterns
- ✓ Exports to mailbox
- ✓ Shows results breakdown

---

## 📊 Quick Stats to Mention

### System Capabilities
- **11 collectors** capturing Windows events
- **3 MCP servers** operational
- **30 CERT r4.2 patterns** (100% research-based)
- **111 events** exported (16 real + 95 simulated)

### Academic Credibility
- **Source**: CMU CERT Insider Threat Test Dataset r4.2
- **Type**: Published research, standard benchmark
- **Credibility**: 100% research-based, 0% hand-crafted

---

## 💬 What to Say

### Opening (30 seconds)
"I built an insider threat detection system with three MCP servers that collect real Windows events, inject attack simulations from the CERT r4.2 dataset, and export clean data for analysis."

### Dataset Explanation (30 seconds)
"The attack patterns come from CMU's CERT r4.2 dataset - a standard benchmark in cybersecurity research. I'm using 30 real insider threat instances covering USB exfiltration, data theft, and keylogger attacks. This ensures academic credibility since every attack is traceable to published research."

### Results (30 seconds)
"The system successfully collected 16 real events from my Windows machine and injected 95 simulated attack events from CERT patterns. All events are properly marked, stored in JSON Lines format, and exported to a clean JSON file ready for behavioral analysis."

---

## 🎬 Demo Flow (5 minutes)

### 1. Show the Test (2 min)
```bash
python test_mcp_full_workflow.py
```
Point out:
- Real event collection (Step 1)
- Storage and querying (Step 2)
- CERT attack injection (Step 3)
- Export to mailbox (Step 4)

### 2. Show the Results (1 min)
```bash
# Event breakdown
python -c "import json; events=json.load(open('mailbox/clean_events.json')); print(f'Total: {len(events)}'); simulated=sum(1 for e in events if e.get('metadata',{}).get('is_simulated')); print(f'Real: {len(events)-simulated}, Simulated: {simulated}')"
```

### 3. Show Sample Attack (1 min)
```bash
# View attack event
python -c "import json; events=json.load(open('mailbox/clean_events.json')); attack=[e for e in events if e.get('metadata',{}).get('is_simulated')][0]; print('Attack Event:'); print(f\"  Type: {attack['event_type']}\"); print(f\"  MITRE: {attack['metadata']['mitre_technique']}\"); print(f\"  Attack: {attack['metadata']['attack_name']}\"); print(f\"  User: {attack['user_id']}\"); print(f\"  Device: {attack['device_id']}\")"
```

### 4. Show Dataset (1 min)
```bash
# Show CERT patterns
python -c "import json; data=json.load(open('data/attacks/attack_patterns.json')); print(f'Total patterns: {len(data[\"attack_patterns\"])}'); print('All from CERT r4.2 dataset'); print('Source: CMU CERT Insider Threat Test Dataset')"
```

---

## 🔑 Key Points to Emphasize

### Technical Achievement
- ✅ Working data collection pipeline
- ✅ Event storage and querying
- ✅ Attack simulation engine
- ✅ Clean data export

### Academic Rigor
- ✅ 100% CERT r4.2 dataset
- ✅ Published research source
- ✅ Reproducible results
- ✅ Standard benchmark

### Practical Results
- ✅ 111 events generated
- ✅ Real + simulated data
- ✅ Properly marked events
- ✅ Ready for analysis

---

## 📁 Files to Show (if asked)

### Main Test
- `test_mcp_full_workflow.py` - Complete workflow test

### Results
- `mailbox/clean_events.json` - 111 exported events
- `mailbox/clean_events_metadata.json` - Export metadata

### Dataset
- `data/attacks/attack_patterns.json` - 30 CERT patterns

### Documentation
- `SYSTEM_READY.md` - Complete system overview
- `ATTACK_INJECTOR_COMPLETE.md` - Attack injector details

---

## ❓ Anticipated Questions & Answers

### Q: "Why CERT dataset?"
**A**: "CERT r4.2 is a standard benchmark in insider threat research from CMU. Using published research data ensures academic credibility and reproducibility, rather than making up attack scenarios."

### Q: "How many attack patterns?"
**A**: "30 real insider threat instances from CERT r4.2, covering three scenarios: USB exfiltration, job hunting data theft, and keylogger impersonation. All mapped to MITRE ATT&CK techniques."

### Q: "Can you show real vs simulated?"
**A**: "Yes, all events have an `is_simulated` flag in metadata. Real events come from collectors with sources like 'psutil', simulated events have source 'attack_simulation' and include MITRE technique, attack type, and attack ID."

### Q: "What collectors do you have?"
**A**: "11 Windows collectors: system, file, network, process, browser, email, Windows events, USB devices, clipboard, registry, and DNS queries."

### Q: "Is this production-ready?"
**A**: "Yes, all tests pass. The system collects real data, injects realistic attacks, stores everything in JSON Lines format, and exports clean JSON for analysis. Three MCP servers are operational."

### Q: "What's next?"
**A**: "The system is ready for Team 2 to use for behavioral analysis. Optional enhancements would be adding enrichment (user/device context) and a visualization dashboard."

---

## 🎯 Closing Statement

"The system demonstrates a complete insider threat detection pipeline with research-based attack simulations. It's production-ready, academically credible, and generates clean data for behavioral analysis."

---

## 🆘 If Something Goes Wrong

### Test fails
```bash
# Check if virtual environment is active
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Run test again
python test_mcp_full_workflow.py
```

### No events collected
- System collector should always return at least 1 event
- If it fails, it's likely a psutil issue: `pip install psutil`

### Can't find files
- Make sure you're in the project root directory
- Check: `ls mailbox/clean_events.json`

---

## ✅ Pre-Demo Checklist

- [ ] Virtual environment activated
- [ ] Run test once to verify: `python test_mcp_full_workflow.py`
- [ ] Check mailbox has events: `ls mailbox/`
- [ ] Review key talking points above
- [ ] Have this cheatsheet open during demo

---

**You're ready! Good luck with your demonstration! 🎉**
