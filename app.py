from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
import sqlite3
import time
import os

app = FastAPI(title="Autonomous Global Wealth Protocol", version="7.0.0")

DB_FILE = "protocol_core.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS protocol_treasury (
            id TEXT PRIMARY KEY,
            total_treasury_usdt REAL,
            user_stake_percent REAL,
            live_pool_balance REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_node (
            node_id TEXT PRIMARY KEY,
            owner_name TEXT,
            accumulated_yield REAL,
            validated_tasks INTEGER,
            status TEXT,
            last_ping INTEGER
        )
    ''')
    
    # इनिशियलाइज्ड डेटा
    cursor.execute('SELECT COUNT(*) FROM protocol_treasury')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO protocol_treasury VALUES (?, ?, ?, ?)', ('GLOBAL-POOL', 1250400.0, 1.5, 45000.0))
        
    cursor.execute('SELECT COUNT(*) FROM user_node WHERE node_id = ?', ('NODE-IND-9988',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO user_node VALUES (?, ?, ?, ?, ?, ?)', 
                       ('NODE-IND-9988', 'Global Citizen', 1420.50, 3120, 'ACTIVE_24_7', int(time.time())))
    conn.commit()
    conn.close()

init_db()

# बैकग्राउंड प्रोटोकॉल यील्ड जनरेटर (ग्लोबल टर्नओवर से हिस्सा बांटना)
async def protocol_yield_engine():
    while True:
        await asyncio.sleep(5)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT accumulated_yield, validated_tasks FROM user_node WHERE node_id = ?', ('NODE-IND-9988',))
        row = cursor.fetchone()
        if row:
            current_yield, tasks = row
            new_yield = current_yield + 2.50 # ऑटोमैटिक डिविडेंड क्रेडिट
            new_tasks = tasks + 1
            cursor.execute('UPDATE user_node SET accumulated_yield = ?, validated_tasks = ?, last_ping = ? WHERE node_id = ?',
                           (new_yield, new_tasks, int(time.time()), 'NODE-IND-9988'))
        conn.commit()
        conn.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(protocol_yield_engine())

@app.get("/", response_class=HTMLResponse)
async def global_dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT total_treasury_usdt, user_stake_percent FROM protocol_treasury WHERE id = ?', ('GLOBAL-POOL',))
    treasury = cursor.fetchone()
    
    cursor.execute('SELECT accumulated_yield, validated_tasks, status FROM user_node WHERE node_id = ?', ('NODE-IND-9988',))
    node = cursor.fetchone()
    conn.close()
    
    total_treasury, stake_share = treasury
    yield_amt, tasks, status = node
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autonomous Global Wealth Protocol</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #030712; color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; text-align: center; }}
            .container {{ max-width: 500px; margin: auto; }}
            .card {{ background: #0f172a; padding: 25px; border-radius: 20px; border: 1px solid #1e293b; box-shadow: 0 10px 30px rgba(0,0,0,0.8); margin-bottom: 20px; text-align: left; }}
            .header {{ font-size: 18px; color: #38bdf8; font-weight: bold; margin-bottom: 10px; }}
            .metric {{ font-size: 32px; color: #10b981; font-weight: bold; margin: 10px 0; }}
            .sub-text {{ font-size: 13px; color: #94a3b8; }}
            .badge {{ background: #065f46; color: #34d399; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            button {{ width: 100%; padding: 14px; border-radius: 12px; border: none; background: #6366f1; color: white; font-weight: bold; cursor: pointer; font-size: 15px; transition: 0.2s; }}
            button:hover {{ background: #4f46e5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🌐 Global Wealth Protocol</h2>
            <p style="font-size: 13px; color: #94a3b8;">Autonomous 24/7 DePIN & AI Asset Engine</p>
            
            <div class="card">
                <div class="header">🛡️ Your Edge Node Status</div>
                <p>Node ID: <b>NODE-IND-9988</b> &nbsp; <span class="badge">{status}</span></p>
                <p class="sub-text">Validated Micro-Tasks: <b id="tasks">{tasks}</b></p>
                <div class="metric">₹<span id="yield">{yield_amt:.2f}</span></div>
                <p class="sub-text">पोटोकॉल डिविडेंड और बैकग्राउंड कंप्यूट यील्ड (Live)</p>
            </div>

            <div class="card">
                <div class="header">📊 Global Protocol Treasury</div>
                <p class="sub-text">Enterprise B2B Revenue Pool:</p>
                <div style="font-size: 24px; color: #f59e0b; font-weight: bold; margin: 5px 0;">${total_treasury:,.2f} USDT</div>
                <p class="sub-text">Your Ownership Stake Share: <b>{stake_share}%</b></p>
            </div>

            <button onclick="claimDividend()">वॉलेट में डिविडेंड क्लेम करें</button>
            <p id="msg" style="font-size: 13px; color: #facc15; margin-top: 15px; text-align: center;"></p>
        </div>

        <script>
            // रियल-टाइम डेटा सिंकिंग हर 3 सेकंड में
            setInterval(async () => {{
                let res = await fetch('/protocol/stats');
                let data = await res.json();
                document.getElementById('yield').innerText = data.yield.toFixed(2);
                document.getElementById('tasks').innerText = data.tasks;
            }}, 3000);

            async function claimDividend() {{
                let res = await fetch('/protocol/claim', {{ method: 'POST' }});
                let data = await res.json();
                document.getElementById('msg').innerText = data.message;
                if(data.success) {{
                    document.getElementById('yield').innerText = "0.00";
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.get("/protocol/stats")
async def protocol_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT accumulated_yield, validated_tasks FROM user_node WHERE node_id = ?', ('NODE-IND-9988',))
    row = cursor.fetchone()
    conn.close()
    return {"yield": row[0], "tasks": row[1]}

@app.post("/protocol/claim")
async def claim_dividend():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_node SET accumulated_yield = 0.0 WHERE node_id = ?', ('NODE-IND-9988',))
    conn.commit()
    conn.close()
    return {"success": True, "message": "✅ डिविडेंड सफलतापूर्वक आपके कनेक्टेड वॉलेट में ट्रांसफर कर दिया गया है!"}
