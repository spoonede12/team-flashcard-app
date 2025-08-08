"""
Simplified single-file FastAPI deployment for team flashcards
This version has minimal dependencies for easier deployment
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import uuid
import shutil
import secrets
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import json

# Simple authentication
VALID_USERNAME = "dave"
VALID_PASSWORD = "india"
active_tokens = set()
security = HTTPBearer()

app = FastAPI(title="Team Flashcard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    # Create decks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create flashcards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            person_name TEXT NOT NULL,
            person_role TEXT NOT NULL,
            image_filename TEXT,
            front TEXT DEFAULT '',
            back TEXT DEFAULT '',
            difficulty INTEGER DEFAULT 3,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            FOREIGN KEY (deck_id) REFERENCES decks (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Authentication functions
def create_access_token():
    token = secrets.token_urlsafe(32)
    active_tokens.add(token)
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return VALID_USERNAME

# Login endpoint
@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    if username != VALID_USERNAME or password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token()
    return {"access_token": access_token, "token_type": "bearer"}

# Get all decks
@app.get("/decks")
def get_decks(current_user: str = Depends(verify_token)):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.id, d.name, d.description, d.created_at, COUNT(f.id) as card_count
        FROM decks d
        LEFT JOIN flashcards f ON d.id = f.deck_id
        GROUP BY d.id, d.name, d.description, d.created_at
        ORDER BY d.created_at DESC
    ''')
    
    decks = []
    for row in cursor.fetchall():
        decks.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "created_at": row[3],
            "card_count": row[4]
        })
    
    conn.close()
    return decks

# Create new deck
@app.post("/decks")
def create_deck(name: str = Form(), description: str = Form(""), current_user: str = Depends(verify_token)):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO decks (name, description) VALUES (?, ?)",
        (name, description)
    )
    
    deck_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": deck_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "card_count": 0
    }

# Root endpoint - serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Team Flashcards</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
            .container { max-width: 400px; margin: 0 auto; background: white; color: black; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            h1 { text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; }
            input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 12px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; padding: 14px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; font-size: 1.1rem; cursor: pointer; margin-top: 20px; }
            button:hover { transform: translateY(-2px); }
            .error { color: red; margin-top: 10px; }
            .success { color: green; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Team Flashcards</h1>
            <div id="loginForm">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="username" placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="password" placeholder="Enter password">
                </div>
                <button onclick="login()">Login</button>
                <div id="message"></div>
            </div>
            <div id="dashboard" style="display:none;">
                <h2>Welcome to Team Flashcards!</h2>
                <p>Your app is running successfully!</p>
                <p>✅ Authentication working</p>
                <p>✅ Database connected</p>
                <p>✅ Ready for team photos</p>
                <button onclick="logout()">Logout</button>
            </div>
        </div>
        
        <script>
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const messageDiv = document.getElementById('message');
                
                try {
                    const formData = new FormData();
                    formData.append('username', username);
                    formData.append('password', password);
                    
                    const response = await fetch('/login', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('token', data.access_token);
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'block';
                        messageDiv.innerHTML = '<div class="success">Login successful!</div>';
                    } else {
                        messageDiv.innerHTML = '<div class="error">Invalid credentials</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="error">Login failed</div>';
                }
            }
            
            function logout() {
                localStorage.removeItem('token');
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('dashboard').style.display = 'none';
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
                document.getElementById('message').innerHTML = '';
            }
            
            // Check if already logged in
            if (localStorage.getItem('token')) {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    # Try multiple ports for Replit compatibility
    port = int(os.environ.get("PORT", os.environ.get("REPL_SLUG", 3000)))
    if isinstance(port, str):
        port = 3000
    
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
