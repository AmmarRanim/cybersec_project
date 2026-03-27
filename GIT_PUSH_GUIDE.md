# Git Push Guide

## Quick Commands

### First Time Setup (if not done)
```bash
# Initialize git (if not already done)
git init

# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git
```

### Push Your Code

```bash
# 1. Check what will be committed
git status

# 2. Add all files
git add .

# 3. Commit with message
git commit -m "Complete insider threat detection system with CERT r4.2 dataset"

# 4. Push to GitHub
git push -u origin main
```

If you get an error about branch name, try:
```bash
git push -u origin master
```

---

## What Will Be Committed

### ✅ Included (Important Files)
- All Python source code (collectors, MCP servers)
- Documentation (*.md files)
- Test scripts
- Attack patterns dataset (attack_patterns.json)
- Configuration files (requirements.txt, mcp_config.json)
- Empty logs directory structure

### ❌ Excluded (Ignored by .gitignore)
- Virtual environment (.venv/)
- Python cache (__pycache__/)
- Log files (logs/*.jsonl, logs/*.log)
- CERT r4.2 dataset (r4.2/ - 15GB, too large)
- Test directories (test_files/)
- OS files (.DS_Store, Thumbs.db)
- IDE files (.vscode/, .idea/)

---

## Important Notes

### CERT Dataset
The CERT r4.2 dataset (15GB) is NOT included in the repository because:
- It's too large for GitHub
- It's publicly available from CMU
- Your attack_patterns.json (extracted patterns) IS included

If someone clones your repo, they can:
1. Download CERT r4.2 from CMU if needed
2. Use your attack_patterns.json directly (already extracted)

### Mailbox Exports
By default, mailbox exports ARE included. If you want to exclude them:
```bash
# Uncomment these lines in .gitignore:
# mailbox/clean_events.json
# mailbox/clean_events_metadata.json
```

### Logs
Log files are excluded, but the logs/ directory structure is kept.

---

## Commit Message Suggestions

### For Initial Commit
```bash
git commit -m "Initial commit: Insider threat detection system with CERT r4.2 integration"
```

### For Complete System
```bash
git commit -m "Complete system: 11 collectors, 3 MCP servers, 30 CERT attack patterns"
```

### Detailed Commit
```bash
git commit -m "Complete insider threat detection system

- 11 Windows data collectors (system, file, network, process, etc.)
- 3 MCP servers (Collector-Executor, Event-Storage, Attack-Injector)
- 30 CERT r4.2 attack patterns (100% research-based)
- Complete test suite with workflow tests
- Comprehensive documentation

System generates realistic attack simulations from CMU CERT dataset
for testing insider threat detection algorithms."
```

---

## Troubleshooting

### "fatal: not a git repository"
```bash
git init
```

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/yourusername/your-repo.git
```

### "Updates were rejected"
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Large files error
If you accidentally try to commit large files:
```bash
# Remove from staging
git reset HEAD path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore
```

---

## After Pushing

### Verify on GitHub
1. Go to your repository on GitHub
2. Check that all files are there
3. Verify README.md displays correctly
4. Check that .gitignore is working (no .venv/, no logs/*.jsonl)

### Clone Test
Test that someone else can use your code:
```bash
# In a different directory
git clone https://github.com/yourusername/your-repo.git
cd your-repo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python test_mcp_full_workflow.py
```

---

## Repository Structure (What Gets Pushed)

```
cybersec_project/
├── .gitignore                    ✅ Included
├── README.md                     ✅ Included (if exists)
├── requirements.txt              ✅ Included
├── mcp_config.json              ✅ Included
├── collectors/                   ✅ Included (all .py files)
├── mcp_servers/                  ✅ Included (all .py files)
├── data/attacks/                 ✅ Included
│   ├── attack_patterns.json     ✅ Included (30 CERT patterns)
│   ├── cert_converter.py        ✅ Included
│   └── *.md                     ✅ Included
├── tests/                        ✅ Included
├── logs/                         ✅ Directory structure only
│   └── .gitkeep                 ✅ Included
├── mailbox/                      ✅ Included (optional)
├── *.md                          ✅ All documentation
├── test_*.py                     ✅ All test scripts
├── .venv/                        ❌ Excluded
├── __pycache__/                  ❌ Excluded
├── logs/*.jsonl                  ❌ Excluded
├── logs/*.log                    ❌ Excluded
└── r4.2/                         ❌ Excluded (15GB)
```

---

## Quick Push (Copy-Paste)

```bash
# Check status
git status

# Add everything
git add .

# Commit
git commit -m "Complete insider threat detection system with CERT r4.2 dataset"

# Push
git push -u origin main
```

Done! 🎉
