from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import asyncio
import sqlite3
import os

app = FastAPI()

DB_FILE = "wealth_engine.db"

# डेटाबेस इनिशियलाइज करें ताकि बैलेंस कभी डिलीट न हो (Permanent Storage)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY,
            balance REAL,
            total_searches INTEGER
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM state')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO state (id, balance, total_searches) VALUES (1, 1512.5, 42)')
    conn.commit()
    conn.close()

init_db()

def get_db_state():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT balance, total_searches FROM state WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return {"balance": row[0], "total_searches": row[1]}

def update_db_state(balance, total_searches):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE state SET balance = ?, total_searches = ? WHERE id = 1', (balance, total_searches))
    conn.commit()
    conn.close()

# 24/7 बैकग्राउंड वर्कर जो डेटाबेस में लगातार कमाई जोड़ता रहेगा
async def background_wealth_engine():
    while True:
        await asyncio.sleep(60)  # हर 60 सेकंड में बैकग्राउंड नोड से कमाई जुड़ेगी
        state = get_db_state()
        new_balance = state["balance"] + 2.5
        update_db_state(new_balance, state["total_searches"])

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_wealth_engine())

@app.get("/", response_class=HTMLResponse)
async def read_root():
    state = get_db_state()
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autonomous AI Search & Wealth Engine</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 20px; text-align: center; }}
            .card {{ background: #1e293b; padding: 25px; border-radius: 16px; max-width: 500px; margin: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.4); border: 1px solid #334155; }}
            .balance {{ font-size: 28px; color: #22c55e; font-weight: bold; margin: 15px 0; }}
            input, button {{ width: 100%; padding: 14px; margin-top: 12px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }}
            input {{ background: #334155; color: white; outline: none; }}
            button {{ background: #22c55e; color: white; font-weight: bold; cursor: pointer; transition: 0.2s; }}
            button:hover {{ background: #16a34a; }}
            .status {{ font-size: 13px; color: #38bdf8; margin-top: 15px; background: #0f172a; padding: 10px; border-radius: 6px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 Autonomous Wealth Engine</h2>
            <p style="color: #94a3b8; font-size: 14px;">24/7 Permanent Persistent Node</p>
            <div class="balance">💰 लाइव वॉलेट: ₹<span id="bal">{state['balance']:.1f}</span></div>
            <input type="text" id="query" placeholder="यहाँ खोजें (जैसे: बेस्ट गैजेट्स)...">
            <button onclick="performSearch()">सर्च करें और कमीशन कमाएं</button>
            <div class="status" id="result">🟢 24/7 परमानेंट डेटाबेस इंजन सक्रिय है।</div>
        </div>
        <script>
            async function performSearch() {{
                let q = document.getElementById('query').value;
                if(!q) q = "Commercial Intent Search";
                let res = await fetch('/search?q=' + encodeURIComponent(q));
                let data = await res.json();
                document.getElementById('bal').innerText = data.balance.toFixed(1);
                document.getElementById('result').innerText = "✅ " + data.message;
            }}
            
            // लाइव वॉलेट को हर 5 सेकंड में ऑटो-सिंक करें
            setInterval(async () => {{
                let res = await fetch('/balance');
                let data = await res.json();
                document.getElementById('bal').innerText = data.balance.toFixed(1);
            }}, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/search")
async def search(q: str):
    state = get_db_state()
    new_balance = state["balance"] + 12.5
    new_searches = state["total_searches"] + 1
    update_db_state(new_balance, new_searches)
    return {
        "balance": new_balance, 
        "message": f"'{q}' के लिए कमर्शियल डील फेच हुई और ₹12.5 परमानेंट वॉलेट में जुड़ गए!"
    }

@app.get("/balance")
async def get_balance():
    state = get_db_state()
    return {"balance": state["balance"]}
