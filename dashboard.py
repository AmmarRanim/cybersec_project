"""
Collector Dashboard — Quick visualization of all collectors.
Run:  .venv\\Scripts\\python dashboard.py
Open: http://localhost:5000
"""

import os
import threading
from flask import Flask, jsonify, render_template_string
from collectors.file_collector import SecurityFileHandler
from watchdog.observers import Observer
import getpass, socket

app = Flask(__name__)

# ── Background File Watcher ────────────────────────────────────────────────
# Starts when the app launches and continuously records file events
file_events_lock = threading.Lock()
file_handler = None
file_observer = None

def start_background_file_watcher():
    global file_handler, file_observer
    user_id = getpass.getuser()
    device_id = socket.gethostname()
    file_handler = SecurityFileHandler(user_id, device_id)
    file_observer = Observer()

    # Watch key user directories
    home = os.path.expanduser("~")
    watch_dirs = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
    ]
    for d in watch_dirs:
        if os.path.isdir(d):
            file_observer.schedule(file_handler, d, recursive=True)

    file_observer.daemon = True
    file_observer.start()
    print(f"   📁 File watcher active on: {', '.join(os.path.basename(d) for d in watch_dirs)}")


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber-Data Genesis — Collector Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0e1a; --surface: #111827; --surface2: #1a2235;
            --border: #1e293b; --accent: #3b82f6;
            --accent-glow: rgba(59,130,246,0.25);
            --green: #22c55e; --red: #ef4444; --orange: #f59e0b;
            --cyan: #06b6d4; --purple: #a855f7;
            --text: #e2e8f0; --text-dim: #94a3b8; --text-muted: #64748b;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }

        .header {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem; display:flex; align-items:center; gap:1rem;
        }
        .header .shield { font-size:2rem; }
        .header h1 {
            font-size:1.4rem; font-weight:600;
            background: linear-gradient(135deg, #3b82f6, #a855f7);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        }
        .header .subtitle { font-size:0.85rem; color:var(--text-dim); margin-top:0.15rem; }

        .main { padding:1.5rem 2rem; max-width:1400px; margin:0 auto; }

        .btn-grid {
            display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
            gap:0.75rem; margin-bottom:1.5rem;
        }
        .btn {
            background:var(--surface); border:1px solid var(--border); border-radius:12px;
            padding:1rem 1.2rem; cursor:pointer; transition:all 0.2s ease;
            display:flex; align-items:center; gap:0.75rem;
            color:var(--text); font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:500;
        }
        .btn:hover {
            border-color:var(--accent); box-shadow:0 0 20px var(--accent-glow);
            transform:translateY(-2px);
        }
        .btn:active { transform:translateY(0); }
        .btn.loading { opacity:0.6; pointer-events:none; }
        .btn .icon { font-size:1.5rem; }
        .btn[data-type="system"] .icon { color:var(--cyan); }
        .btn[data-type="network"] .icon { color:var(--green); }
        .btn[data-type="process"] .icon { color:var(--orange); }
        .btn[data-type="file"] .icon { color:var(--red); }
        .btn[data-type="browser"] .icon { color:var(--purple); }
        .btn[data-type="email"] .icon { color:#3b82f6; }
        .btn[data-type="eventlog"] .icon { color:#8b5cf6; }
        .btn[data-type="usb"] .icon { color:#ec4899; }
        .btn[data-type="registry"] .icon { color:#f59e0b; }
        .btn[data-type="all"] {
            background:linear-gradient(135deg, #1e3a5f, #2d1b69);
            border-color:var(--accent);
        }
        .btn[data-type="all"] .icon { color:var(--accent); }

        .controls-bar {
            background:var(--surface); border:1px solid var(--border); border-radius:10px;
            padding:0.75rem 1.2rem; margin-bottom:0.75rem;
            display:flex; align-items:center; gap:1.5rem; font-size:0.85rem;
        }
        .time-range-control {
            display:flex; align-items:center; gap:0.75rem;
        }
        .time-range-control label {
            color:var(--text-dim); font-weight:500;
        }
        .time-range-control input[type="range"] {
            width:200px; height:6px; border-radius:3px;
            background:var(--border); outline:none;
            -webkit-appearance:none;
        }
        .time-range-control input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance:none; appearance:none;
            width:16px; height:16px; border-radius:50%;
            background:var(--accent); cursor:pointer;
            box-shadow:0 0 8px var(--accent-glow);
        }
        .time-range-control input[type="range"]::-moz-range-thumb {
            width:16px; height:16px; border-radius:50%;
            background:var(--accent); cursor:pointer; border:none;
            box-shadow:0 0 8px var(--accent-glow);
        }
        #hours-display {
            color:var(--accent); font-weight:600; min-width:80px;
        }
        .time-hint {
            color:var(--text-muted); font-size:0.75rem; margin-left:1rem;
        }

        .status-bar {
            background:var(--surface); border:1px solid var(--border); border-radius:10px;
            padding:0.75rem 1.2rem; margin-bottom:1rem;
            display:flex; align-items:center; gap:1rem; font-size:0.85rem;
        }
        .status-dot {
            width:8px; height:8px; border-radius:50%; background:var(--green);
            box-shadow:0 0 8px rgba(34,197,94,0.5); animation:pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .event-count { margin-left:auto; color:var(--accent); font-weight:600; }

        .table-wrap {
            background:var(--surface); border:1px solid var(--border);
            border-radius:12px; overflow:hidden;
        }
        .table-scroll { overflow-x:auto; max-height:60vh; overflow-y:auto; }

        table { width:100%; border-collapse:collapse; font-size:0.82rem; }
        thead { background:var(--surface2); position:sticky; top:0; z-index:1; }
        th {
            padding:0.7rem 1rem; text-align:left; font-weight:600; color:var(--text-dim);
            text-transform:uppercase; font-size:0.72rem; letter-spacing:0.05em;
            border-bottom:1px solid var(--border); white-space:nowrap;
        }
        td {
            padding:0.6rem 1rem; border-bottom:1px solid var(--border); color:var(--text);
            max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
        }
        tr:hover td { background:rgba(59,130,246,0.05); }

        .badge {
            display:inline-block; padding:0.15rem 0.5rem; border-radius:6px;
            font-size:0.72rem; font-weight:600;
        }
        .badge-system { background:rgba(6,182,212,0.15); color:var(--cyan); }
        .badge-network { background:rgba(34,197,94,0.15); color:var(--green); }
        .badge-process { background:rgba(245,158,11,0.15); color:var(--orange); }
        .badge-file { background:rgba(239,68,68,0.15); color:var(--red); }
        .badge-web { background:rgba(168,85,247,0.15); color:var(--purple); }
        .badge-device { background:rgba(59,130,246,0.15); color:var(--accent); }

        .empty-state { text-align:center; padding:4rem 2rem; color:var(--text-muted); }
        .empty-state .icon { font-size:3rem; margin-bottom:1rem; }

        .spinner {
            display:inline-block; width:16px; height:16px;
            border:2px solid var(--border); border-top-color:var(--accent);
            border-radius:50%; animation:spin 0.6s linear infinite;
        }
        @keyframes spin { to { transform:rotate(360deg); } }

        .file-hint {
            background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2);
            border-radius:8px; padding:0.5rem 1rem; margin-bottom:1rem;
            font-size:0.8rem; color:var(--red); display:none;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="shield">🛡️</div>
        <div>
            <h1>Cyber-Data Genesis</h1>
            <div class="subtitle">Team 1 — Collector Visualization Dashboard</div>
        </div>
    </div>
    <div class="main">
        <div class="btn-grid">
            <button class="btn" data-type="system" onclick="collect('system')">
                <span class="icon">🖥️</span>
                <div><div>System</div><div style="font-size:0.7rem;color:var(--text-muted)">Login, idle time</div></div>
            </button>
            <button class="btn" data-type="network" onclick="collect('network')">
                <span class="icon">🌐</span>
                <div><div>Network</div><div style="font-size:0.7rem;color:var(--text-muted)">TCP/UDP connections</div></div>
            </button>
            <button class="btn" data-type="process" onclick="collect('process')">
                <span class="icon">⚙️</span>
                <div><div>Process</div><div style="font-size:0.7rem;color:var(--text-muted)">Running procs, LOLBins</div></div>
            </button>
            <button class="btn" data-type="file" onclick="collect('file')">
                <span class="icon">📁</span>
                <div><div>File</div><div style="font-size:0.7rem;color:var(--text-muted)">Live: create, delete, move</div></div>
            </button>
            <button class="btn" data-type="browser" onclick="collect('browser')">
                <span class="icon">🔍</span>
                <div><div>Browser</div><div style="font-size:0.7rem;color:var(--text-muted)">Chrome/Edge history</div></div>
            </button>
            <button class="btn" data-type="email" onclick="collect('email')">
                <span class="icon">�</span>
                <div><div>Email</div><div style="font-size:0.7rem;color:var(--text-muted)">Outlook sent/received</div></div>
            </button>
            <button class="btn" data-type="eventlog" onclick="collect('eventlog')">
                <span class="icon">📋</span>
                <div><div>Event Log</div><div style="font-size:0.7rem;color:var(--text-muted)">Security events</div></div>
            </button>
            <button class="btn" data-type="usb" onclick="collect('usb')">
                <span class="icon">💾</span>
                <div><div>USB History</div><div style="font-size:0.7rem;color:var(--text-muted)">Device tracking</div></div>
            </button>
            <button class="btn" data-type="registry" onclick="collect('registry')">
                <span class="icon">🔑</span>
                <div><div>Registry</div><div style="font-size:0.7rem;color:var(--text-muted)">Persistence keys</div></div>
            </button>
            <button class="btn" data-type="dns" onclick="collect('dns')">
                <span class="icon">🌍</span>
                <div><div>DNS Queries</div><div style="font-size:0.7rem;color:var(--text-muted)">C2 detection, DGA</div></div>
            </button>
            <button class="btn" data-type="all" onclick="collect('all')">
                <span class="icon">🚀</span>
                <div><div>Collect All</div><div style="font-size:0.7rem;color:var(--text-muted)">Run everything</div></div>
            </button>
        </div>

        <div class="file-hint" id="file-hint">
            📁 File watcher is running in the background on Desktop, Documents, Downloads.
            Create, move, or delete a file, then click the File button to see the events.
        </div>

        <div class="controls-bar">
            <div class="time-range-control">
                <label for="hours-slider">Time Range:</label>
                <input type="range" id="hours-slider" min="1" max="720" value="48" step="1">
                <span id="hours-display">48 hours</span>
                <span class="time-hint">⚠️ Affects: Email, Browser, Event Log</span>
            </div>
        </div>

        <div class="status-bar">
            <div class="status-dot"></div>
            <span id="status-text">Ready — file watcher running in background</span>
            <span class="event-count" id="event-count"></span>
        </div>
        <div class="table-wrap">
            <div class="table-scroll" id="table-container">
                <div class="empty-state">
                    <div class="icon">📊</div>
                    <p>Select a collector above to see live data from your PC</p>
                </div>
            </div>
        </div>
    </div>
    <script>
        const badgeClass = {
            system:'badge-system', network:'badge-network', process:'badge-process',
            file:'badge-file', web:'badge-web', device:'badge-device', email:'badge-system'
        };
        // Show file hint on page load
        document.getElementById('file-hint').style.display = 'block';

        // Time range slider
        const slider = document.getElementById('hours-slider');
        const display = document.getElementById('hours-display');
        slider.addEventListener('input', (e) => {
            const hours = parseInt(e.target.value);
            if (hours < 24) {
                display.textContent = `${hours} hour${hours !== 1 ? 's' : ''}`;
            } else if (hours < 168) {
                display.textContent = `${Math.round(hours / 24)} days`;
            } else {
                display.textContent = `${Math.round(hours / 168)} weeks`;
            }
        });

        async function collect(type) {
            const btn = document.querySelector(`[data-type="${type}"]`);
            const statusEl = document.getElementById('status-text');
            const countEl = document.getElementById('event-count');
            const hoursBack = parseInt(slider.value);
            
            btn.classList.add('loading');
            statusEl.innerHTML = `<span class="spinner"></span> Collecting ${type}...`;
            countEl.textContent = '';
            try {
                const res = await fetch(`/api/collect/${type}?hours_back=${hoursBack}`);
                const data = await res.json();
                if (data.error) { statusEl.textContent = `Error: ${data.error}`; return; }
                statusEl.textContent = `✅ ${type} collection complete`;
                countEl.textContent = `${data.events.length} events`;
                renderTable(data.events);
            } catch(e) { statusEl.textContent = `Error: ${e.message}`; }
            finally { btn.classList.remove('loading'); }
        }
        function renderTable(events) {
            if (!events.length) {
                document.getElementById('table-container').innerHTML =
                    '<div class="empty-state"><div class="icon">🔍</div><p>No events captured yet. Try creating, moving, or deleting a file first.</p></div>';
                return;
            }
            let html = `<table><thead><tr>
                <th>Time</th><th>Category</th><th>Type</th>
                <th>Action</th><th>Resource</th><th>Source</th><th>Detail</th>
            </tr></thead><tbody>`;
            events.forEach(e => {
                const m = e.metadata || {};
                const cls = badgeClass[e.event_category] || 'badge-system';
                const time = e.timestamp ? e.timestamp.split('T')[1]?.substring(0,8) || '' : '';
                html += `<tr>
                    <td>${time}</td>
                    <td><span class="badge ${cls}">${e.event_category}</span></td>
                    <td>${e.event_type}</td>
                    <td>${e.action}</td>
                    <td title="${e.resource}">${trunc(e.resource,50)}</td>
                    <td>${e.source}</td>
                    <td title="${getDetail(e)}">${trunc(getDetail(e),40)}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            document.getElementById('table-container').innerHTML = html;
        }
        function getDetail(e) {
            const m = e.metadata || {};
            if (m.idle_time_seconds != null)
                return `idle:${m.idle_time_seconds.toFixed(1)}s session:${(m.session_duration_minutes||0).toFixed(0)}min`;
            if (m.dst_ip) return `${m.src_ip}:${m.src_port}→${m.dst_ip}:${m.dst_port} ${m.protocol} [${m.process_name||'?'}]`;
            if (m.pid != null) return `PID${m.pid} CPU${m.cpu_percent}% MEM${(m.memory_mb||0).toFixed(0)}MB`;
            if (m.file_path) return `${m.file_extension||''} ${m.file_size_bytes?(m.file_size_bytes/1024).toFixed(1)+'KB':'?'} sens:${m.sensitivity_level??'?'}`;
            if (m.domain) return `${m.domain} (${m.visit_count||0} visits)`;
            // Email details
            if (e.event_type === 'email_sent') {
                const recipients = m.email_recipients || '(unknown)';
                return `To: ${recipients} | Ext: ${m.external_recipient_count||0}/${m.recipient_count||0} | Attach: ${m.attachment_count||0}`;
            }
            if (e.event_type === 'email_received') {
                return `From: ${m.sender_email||'?'} | Attach: ${m.attachment_count||0} | ${m.is_external?'[EXTERNAL]':'[INTERNAL]'}`;
            }
            return '';
        }
        function trunc(s,n) { return s && s.length>n ? s.substring(0,n)+'…' : (s||''); }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/collect/<collector_type>")
def api_collect(collector_type):
    from flask import request
    try:
        # Get hours_back parameter from query string (default to 48)
        hours_back = int(request.args.get('hours_back', 48))
        
        events = []
        if collector_type in ("system","all"):
            from collectors.system_collector import collect_system_snapshot
            events.extend(collect_system_snapshot())
        if collector_type in ("network","all"):
            from collectors.network_collector import collect_network_connections
            events.extend(collect_network_connections())
        if collector_type in ("process","all"):
            from collectors.process_collector import collect_running_processes
            events.extend(collect_running_processes())
        if collector_type in ("file","all"):
            # Return real-time events from background watcher
            with file_events_lock:
                events.extend(list(file_handler.collected_events))
        if collector_type in ("browser","all"):
            from collectors.browser_collector import collect_browser_history
            events.extend(collect_browser_history(hours_back=hours_back))
        if collector_type in ("email","all"):
            from collectors.email_collector import collect_outlook_emails
            events.extend(collect_outlook_emails(hours_back=hours_back))
        if collector_type in ("eventlog","all"):
            from collectors.windows_event_collector import collect_windows_events
            events.extend(collect_windows_events(hours_back=hours_back, max_events=100))
        if collector_type in ("usb","all"):
            from collectors.usb_device_collector import collect_usb_device_history
            events.extend(collect_usb_device_history())
        if collector_type in ("registry","all"):
            from collectors.registry_collector import collect_persistence_mechanisms
            events.extend(collect_persistence_mechanisms())
        if collector_type in ("dns","all"):
            from collectors.dns_collector import collect_dns_queries
            events.extend(collect_dns_queries())
        return jsonify({"collector":collector_type, "count":len(events),
                        "events":[e.model_dump() for e in events]})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    print("\n🛡️  Cyber-Data Genesis — Collector Dashboard")
    print("   Open: http://localhost:5000")
    start_background_file_watcher()
    print()
    app.run(debug=True, port=5000, use_reloader=False)
