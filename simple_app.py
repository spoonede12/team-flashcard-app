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
async def create_deck(request_data: dict, current_user: str = Depends(verify_token)):
    name = request_data.get("name", "")
    description = request_data.get("description", "")
    
    if not name:
        raise HTTPException(status_code=400, detail="Deck name is required")
    
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

# Bulk upload endpoint
@app.post("/bulk-upload")
async def bulk_upload_photos(
    deck_id: int = Form(),
    files: List[UploadFile] = File(...),
    current_user: str = Depends(verify_token)
):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    uploaded_count = 0
    
    for file in files:
        if file.content_type and file.content_type.startswith('image/'):
            # Parse filename to extract name and role
            filename = file.filename
            name_part = filename.rsplit('.', 1)[0]  # Remove extension
            
            if ' - ' in name_part:
                person_name, person_role = name_part.split(' - ', 1)
            else:
                person_name = name_part
                person_role = "Team Member"
            
            # Save file
            file_id = str(uuid.uuid4())
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            new_filename = f"{file_id}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, new_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create flashcard record
            cursor.execute('''
                INSERT INTO flashcards (deck_id, person_name, person_role, image_filename, front, back)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (deck_id, person_name, person_role, new_filename, person_name, person_role))
            
            uploaded_count += 1
    
    conn.commit()
    conn.close()
    
    return {"message": f"Successfully uploaded {uploaded_count} photos"}

# Get cards for study
@app.get("/decks/{deck_id}/study")
def get_study_cards(deck_id: int, current_user: str = Depends(verify_token)):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, person_name, person_role, image_filename, front, back
        FROM flashcards 
        WHERE deck_id = ?
        ORDER BY RANDOM()
        LIMIT 20
    ''', (deck_id,))
    
    cards = []
    for row in cursor.fetchall():
        image_url = f"/uploads/{row[3]}" if row[3] else None
        cards.append({
            "id": row[0],
            "front": row[4] or row[1],
            "back": row[5] or row[2],
            "image_url": image_url
        })
    
    conn.close()
    return cards

# Record card review
@app.post("/cards/{card_id}/review")
async def review_card(
    card_id: int,
    request_data: dict,
    current_user: str = Depends(verify_token)
):
    difficulty = request_data.get("difficulty", "medium")
    
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    
    # Simple spaced repetition algorithm
    difficulty_map = {"easy": 1, "medium": 3, "hard": 5}
    difficulty_score = difficulty_map.get(difficulty, 3)
    
    # Calculate next review date
    days_to_add = {1: 3, 3: 1, 5: 0.5}[difficulty_score]
    next_review = datetime.now() + timedelta(days=days_to_add)
    
    cursor.execute('''
        UPDATE flashcards 
        SET difficulty = ?, last_reviewed = ?, next_review = ?, review_count = review_count + 1
        WHERE id = ?
    ''', (difficulty_score, datetime.now().isoformat(), next_review.isoformat(), card_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "success"}

# Serve uploaded images
@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

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
                
                <div id="mainMenu">
                    <button onclick="showCreateDeck()">📚 Create New Deck</button>
                    <button onclick="showBulkUpload()">📤 Bulk Upload Photos</button>
                    <button onclick="showDecks()">🎯 Study Decks</button>
                    <button onclick="logout()">🚪 Logout</button>
                </div>
                
                <div id="createDeckForm" style="display:none;">
                    <h3>Create New Deck</h3>
                    <div class="form-group">
                        <label>Deck Name</label>
                        <input type="text" id="deckName" placeholder="e.g., India Team 2025">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" id="deckDesc" placeholder="Team member photos and roles">
                    </div>
                    <button onclick="createDeck()">Create Deck</button>
                    <button onclick="showMainMenu()">Cancel</button>
                </div>
                
                <div id="bulkUploadForm" style="display:none;">
                    <h3>Bulk Upload Team Photos</h3>
                    <p>Upload photos named like: "John Doe - Software Engineer.jpg"</p>
                    <div class="form-group">
                        <label>Select Deck</label>
                        <select id="uploadDeckSelect">
                            <option value="">Choose a deck...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Upload Photos</label>
                        <input type="file" id="photoFiles" multiple accept="image/*">
                    </div>
                    <button onclick="uploadPhotos()">Upload Photos</button>
                    <button onclick="showMainMenu()">Cancel</button>
                </div>
                
                <div id="decksList" style="display:none;">
                    <h3>Your Decks</h3>
                    <div id="decksContainer"></div>
                    <button onclick="showMainMenu()">Back to Menu</button>
                </div>
                
                <div id="studyMode" style="display:none;">
                    <h3 id="studyDeckName">Study Session</h3>
                    <div id="flashcard" style="text-align:center; padding:20px; border:2px solid #ccc; border-radius:10px; margin:20px 0;">
                        <div id="cardImage"></div>
                        <div id="cardText"></div>
                        <button id="flipButton" onclick="flipCard()">Show Answer</button>
                    </div>
                    <div id="studyControls" style="display:none;">
                        <button onclick="rateCard('easy')">😊 Easy</button>
                        <button onclick="rateCard('medium')">🤔 Medium</button>
                        <button onclick="rateCard('hard')">😵 Hard</button>
                    </div>
                    <button onclick="showMainMenu()">End Study Session</button>
                </div>
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
                showMainMenu();
            }
            
            function showMainMenu() {
                document.getElementById('mainMenu').style.display = 'block';
                document.getElementById('createDeckForm').style.display = 'none';
                document.getElementById('bulkUploadForm').style.display = 'none';
                document.getElementById('decksList').style.display = 'none';
                document.getElementById('studyMode').style.display = 'none';
            }
            
            function showCreateDeck() {
                document.getElementById('mainMenu').style.display = 'none';
                document.getElementById('createDeckForm').style.display = 'block';
            }
            
            function showBulkUpload() {
                document.getElementById('mainMenu').style.display = 'none';
                document.getElementById('bulkUploadForm').style.display = 'block';
                loadDecks();
            }
            
            function showDecks() {
                document.getElementById('mainMenu').style.display = 'none';
                document.getElementById('decksList').style.display = 'block';
                loadDecksList();
            }
            
            async function createDeck() {
                const name = document.getElementById('deckName').value;
                const description = document.getElementById('deckDesc').value;
                
                if (!name) {
                    alert('Please enter a deck name');
                    return;
                }
                
                try {
                    const response = await fetch('/decks', {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token'),
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({name: name, description: description})
                    });
                    
                    if (response.ok) {
                        alert('Deck created successfully!');
                        document.getElementById('deckName').value = '';
                        document.getElementById('deckDesc').value = '';
                        showMainMenu();
                    } else {
                        alert('Failed to create deck');
                    }
                } catch (error) {
                    alert('Error creating deck');
                }
            }
            
            async function loadDecks() {
                try {
                    const response = await fetch('/decks', {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        }
                    });
                    
                    if (response.ok) {
                        const decks = await response.json();
                        const select = document.getElementById('uploadDeckSelect');
                        select.innerHTML = '<option value="">Choose a deck...</option>';
                        decks.forEach(deck => {
                            select.innerHTML += `<option value="${deck.id}">${deck.name}</option>`;
                        });
                    }
                } catch (error) {
                    console.error('Error loading decks');
                }
            }
            
            async function loadDecksList() {
                try {
                    const response = await fetch('/decks', {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        }
                    });
                    
                    if (response.ok) {
                        const decks = await response.json();
                        const container = document.getElementById('decksContainer');
                        container.innerHTML = '';
                        decks.forEach(deck => {
                            container.innerHTML += `
                                <div style="border:1px solid #ccc; padding:10px; margin:10px 0; border-radius:5px;">
                                    <h4>${deck.name}</h4>
                                    <p>${deck.description || 'No description'}</p>
                                    <button onclick="startStudy(${deck.id}, '${deck.name}')">Study This Deck</button>
                                </div>
                            `;
                        });
                    }
                } catch (error) {
                    console.error('Error loading decks');
                }
            }
            
            async function uploadPhotos() {
                const deckId = document.getElementById('uploadDeckSelect').value;
                const files = document.getElementById('photoFiles').files;
                
                if (!deckId) {
                    alert('Please select a deck');
                    return;
                }
                
                if (files.length === 0) {
                    alert('Please select photos to upload');
                    return;
                }
                
                const formData = new FormData();
                formData.append('deck_id', deckId);
                
                for (let file of files) {
                    formData.append('files', file);
                }
                
                try {
                    const response = await fetch('/bulk-upload', {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: formData
                    });
                    
                    if (response.ok) {
                        alert('Photos uploaded successfully!');
                        document.getElementById('photoFiles').value = '';
                        showMainMenu();
                    } else {
                        alert('Failed to upload photos');
                    }
                } catch (error) {
                    alert('Error uploading photos');
                }
            }
            
            let currentCards = [];
            let currentCardIndex = 0;
            let isFlipped = false;
            
            async function startStudy(deckId, deckName) {
                try {
                    const response = await fetch(`/decks/${deckId}/study`, {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        }
                    });
                    
                    if (response.ok) {
                        currentCards = await response.json();
                        if (currentCards.length === 0) {
                            alert('No cards in this deck to study!');
                            return;
                        }
                        
                        currentCardIndex = 0;
                        document.getElementById('studyDeckName').textContent = `Studying: ${deckName}`;
                        document.getElementById('mainMenu').style.display = 'none';
                        document.getElementById('decksList').style.display = 'none';
                        document.getElementById('studyMode').style.display = 'block';
                        showCard();
                    }
                } catch (error) {
                    alert('Error loading study cards');
                }
            }
            
            function showCard() {
                if (currentCardIndex >= currentCards.length) {
                    alert('Study session complete!');
                    showMainMenu();
                    return;
                }
                
                const card = currentCards[currentCardIndex];
                isFlipped = false;
                
                document.getElementById('cardImage').innerHTML = card.image_url ? 
                    `<img src="${card.image_url}" style="max-width:200px; max-height:200px; border-radius:10px;">` : 
                    '<div style="width:200px; height:200px; background:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:10px;">No Image</div>';
                
                document.getElementById('cardText').innerHTML = '<h3>Who is this?</h3>';
                document.getElementById('flipButton').style.display = 'block';
                document.getElementById('studyControls').style.display = 'none';
            }
            
            function flipCard() {
                if (!isFlipped) {
                    const card = currentCards[currentCardIndex];
                    document.getElementById('cardText').innerHTML = `<h3>${card.front}</h3><p>${card.back}</p>`;
                    document.getElementById('flipButton').style.display = 'none';
                    document.getElementById('studyControls').style.display = 'block';
                    isFlipped = true;
                }
            }
            
            async function rateCard(difficulty) {
                const card = currentCards[currentCardIndex];
                
                try {
                    await fetch(`/cards/${card.id}/review`, {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token'),
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({difficulty: difficulty})
                    });
                } catch (error) {
                    console.error('Error recording review');
                }
                
                currentCardIndex++;
                showCard();
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
    # Replit port configuration
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Server will be available at http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
