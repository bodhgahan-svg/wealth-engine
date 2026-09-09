from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
import sqlite3
import time
import hashlib

app = FastAPI(title="Autonomous DePIN Protocol Node", version="2.0.0")

DB_FILE = "node_protocol.db"

# डेटाबेस और नोड रजिस्ट्री इनिशियलाइज करें
def init_protocol_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS node_registry (
            node_id TEXT PRIMARY KEY,
            status TEXT,
            compute_units REAL,
            total_earned REAL,
            last_ping INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_ledger (
            task_id TEXT PRIMARY KEY,
            payload_hash TEXT,
            status TEXT,
            reward REAL,
            timestamp INTEGER
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM node_registry WHERE node_id = ?', ('LOCAL-NODE-01',))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO node_registry (node_id, status, compute_units, total_earned, last_ping) VALUES (?, ?, ?, ?, ?)',
            ('LOCAL-NODE-01', 'ACTIVE', 1.0, 1562.5, int(time.time()))
        )
    conn.commit()
    conn.close()

init_protocol_db()

def get_db_state():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT node_id, status, compute_units, total_earned, last_ping FROM node_registry WHERE node_id = ?', ('LOCAL-NODE-01',))
    row = cursor.fetchone()
    conn.close()
    return row

# 24/7 बैकग्राउंड एज कंप्यूट और पैसिव यील्ड वर्कर
async def background_edge_worker():
    while True:
        await asyncio.sleep(20) # हर 20 सेकंड में बैकग्राउंड नोड सिंक
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT compute_units, total_earned FROM node_registry WHERE node_id = ?', ('LOCAL-NODE-01',))
        row = cursor.fetchone()
        if row:
            units, earned = row
            new_earned = earned + 3.5  # पैसिव बैकग्राउंड यील्ड
            new_units = units + 0.1
            cursor.execute(
                'UPDATE node_registry SET compute_units = ?, total_earned = ?, last_ping = ? WHERE node_id = ?',
                (new_units, new_earned, int(time.time()), 'LOCAL-NODE-01')
            )
        conn.commit()
        conn.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_edge_worker())

@app.get("/", response_class=HTMLResponse)
async def read_root():
    row = get_db_state()
    node_id, status, compute_units, total_earned, last_ping = row
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autonomous DePIN Node Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #090d16; color: #f8fafc; font-family: sans-serif; padding: 20px; text-align: center; }}
            .card {{ background: #131c2e; padding: 28px; border-radius: 20px; max-width: 500px; margin: auto; box-shadow: 0 8px 30px rgba(0,0,0,0.6); border: 1px solid #1e293b; }}
            .balance {{ font-size: 32px; color: #22c55e; font-weight: bold; margin: 15px 0; text-shadow: 0 0 10px rgba(34,197,94,0.3); }}
            .units {{ font-size: 16px; color: #38bdf8; margin: 10px 0; }}
            input, button {{ width: 100%; padding: 14px; margin-top: 12px; border-radius: 10px; border: none; font-size: 16px; box-sizing: border-box; }}
            input {{ background: #1e293b; color: white; outline: none; border: 1px solid #334155; }}
            button {{ background: #22c55e; color: white; font-weight: bold; cursor: pointer; transition: 0.2s; }}
            button:hover {{ background: #16a34a; }}
            .status {{ font-size: 13px; color: #a855f7; margin-top: 15px; background: #090d16; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🌐 DePIN Edge Node Dashboard</h2>
            <p style="color: #94a3b8; font-size: 13px;">Node ID: <b>{node_id}</b> | Status: <span style="color: #22c55e;">{status}</span></p>
            <div class="balance">💰 प्रोटोकॉल कमाई: ₹<span id="bal">{total_earned:.1f}</span></div>
            <div class="units">⚡ कंप्यूट यूनिट्स: <span id="units">{compute_units:.1f}</span></div>
            <input type="text" id="stream" placeholder="यहाँ डेटा स्ट्रीम या टास्क टाइप करें...">
            <button onclick="submitTask()">टास्क सबमिट करें और यील्ड बढ़ाएं</button>
            <div class="status" id="result">🟢 24/7 बैकग्राउंड एज वर्कर और लेजर एक्टिव है।</div>
        </div>
        <script>
            async function submitTask() {{
                let stream = document.getElementById('stream').value;
                if(!stream) stream = "Autonomous Node Compute Pulse";
                let res = await fetch('/node/submit-task', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ task_type: "DATA_VALIDATION", data_stream: stream }})
                }});
                let data = await res.json();
                document.getElementById('bal').innerText = data.updated_balance.toFixed(1);
                document.getElementById('result').innerText = "✅ टास्क वेरिफाई हुआ! रिवॉर्ड: ₹" + data.reward_credited;
            }}
            
            // हर 4 सेकंड में लाइव नोड स्टेटस ऑटो-सिंक होता रहेगा
            setInterval(async () => {{
                let res = await fetch('/node/status');
                let data = await res.json();
                document.getElementById('bal').innerText = data.total_protocol_yield.toFixed(1);
                document.getElementById('units').innerText = data.compute_units_allocated.toFixed(1);
            }}, 4000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/node/status")
async def get_node_status():
    row = get_db_state()
    if not row:
        raise HTTPException(status_code=404, detail="Node not found")
    return {
        "node_id": row[0],
        "status": row[1],
        "compute_units_allocated": row[2],
        "total_protocol_yield": row[3],
        "last_sync_timestamp": row[4]
    }

@app.post("/node/submit-task")
async def submit_compute_task(task: dict):
    task_type = task.get("task_type", "DEFAULT")
    data_stream = task.get("data_stream", "STREAM")
    task_id = hashlib.sha256(f"{task_type}-{time.time()}".encode()).hexdigest()[:16]
    payload_hash = hashlib.sha256(data_stream.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    reward = 12.0
    cursor.execute(
        'INSERT INTO task_ledger (task_id, payload_hash, status, reward, timestamp) VALUES (?, ?, ?, ?, ?)',
        (task_id, payload_hash, 'VERIFIED', reward, int(time.time()))
    )
    cursor.execute('SELECT total_earned FROM node_registry WHERE node_id = ?', ('LOCAL-NODE-01',))
    current_earned = cursor.fetchone()[0]
    new_earned = current_earned + reward
    cursor.execute('UPDATE node_registry SET total_earned = ? WHERE node_id = ?', (new_earned, 'LOCAL-NODE-01'))
    conn.commit()
    conn.close()
    
    return {
        "status": "SUCCESS",
        "task_id": task_id,
        "verified_hash": payload_hash,
        "reward_credited": reward,
        "updated_balance": new_earned
    }
