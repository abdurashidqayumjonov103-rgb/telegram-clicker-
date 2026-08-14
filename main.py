import os
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import database as db

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

db.init_db()

last_clicks = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/auth")
async def authenticate(request: Request):
    body = await request.json()
    init_data = body.get("initData")
    
    user_info = db.verify_telegram_data(init_data, BOT_TOKEN)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Telegram Auth")
    
    user_id = user_info.get("id")
    username = user_info.get("username", "NoUsername")
    ref_id = body.get("start_param")
    
    user = db.get_or_create_user(user_id, username, int(ref_id) if ref_id and ref_id.isdigit() else None)
    return {"status": "success", "user": user}

@app.post("/api/click")
async def process_click(request: Request):
    body = await request.json()
    init_data = body.get("initData")
    user_info = db.verify_telegram_data(init_data, BOT_TOKEN)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_id = user_info.get("id")
    
    now = time.time()
    if user_id in last_clicks and (now - last_clicks[user_id]) < 0.1:
        raise HTTPException(status_code=429, detail="Too fast clicks")
    last_clicks[user_id] = now
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, click_level FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    add_amount = user["click_level"]
    new_balance = user["balance"] + add_amount
    
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
    
    return {"status": "success", "balance": new_balance, "added": add_amount}

@app.post("/api/upgrade")
async def upgrade_click(request: Request):
    body = await request.json()
    init_data = body.get("initData")
    user_info = db.verify_telegram_data(init_data, BOT_TOKEN)
    if not user_info:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user_id = user_info.get("id")
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, click_level FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    cost = user["click_level"] * 100
    if user["balance"] >= cost:
        new_balance = user["balance"] - cost
        new_level = user["click_level"] + 1
        cursor.execute("UPDATE users SET balance = ?, click_level = ? WHERE user_id = ?", (new_balance, new_level, user_id))
        conn.commit()
        conn.close()
        return {"status": "success", "balance": new_balance, "level": new_level, "cost": new_level * 100}
    
    conn.close()
    raise HTTPException(status_code=400, detail="Mabla'g yetarli emas")

@app.get("/api/leaderboard")
async def leaderboard():
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
    top_users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"leaderboard": top_users}

@app.post("/api/admin")
async def admin_stats(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    
    if int(user_id) != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Access denied")
        
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_users, SUM(balance) as total_coins FROM users")
    stats = dict(cursor.fetchone())
    conn.close()
    return 
