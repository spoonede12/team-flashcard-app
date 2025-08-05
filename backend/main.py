from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import uuid
import shutil

# Authentication configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hardcoded credentials (for simplicity)
VALID_USERNAME = "dave"
VALID_PASSWORD = "india"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./flashcards.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, index=True)
    front = Column(Text)  # This will now store the image filename
    back = Column(Text)   # This will store JSON with name, role, and other info
    person_name = Column(String)  # Person's name
    person_role = Column(String)  # Person's role in organization
    image_filename = Column(String)  # Image file path
    difficulty = Column(Integer, default=1)  # 1-5 scale
    last_reviewed = Column(DateTime)
    next_review = Column(DateTime)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    if token_data.username != VALID_USERNAME:
        raise credentials_exception
    return token_data.username

# Pydantic models
class DeckCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DeckResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    card_count: int = 0

class FlashcardCreate(BaseModel):
    deck_id: int
    person_name: str
    person_role: str
    front: Optional[str] = None  # Optional description for the front
    back: Optional[str] = None   # Optional additional info for the back

class FlashcardResponse(BaseModel):
    id: int
    deck_id: int
    front: Optional[str]
    back: Optional[str]
    person_name: str
    person_role: str
    image_filename: Optional[str]
    difficulty: int
    last_reviewed: Optional[datetime]
    next_review: Optional[datetime]
    review_count: int

class ReviewResult(BaseModel):
    card_id: int
    difficulty: int  # 1 (hard) to 5 (easy)

# FastAPI app
app = FastAPI(title="Flashcard API", version="1.0.0")

# Mount static files for image serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Check if we're in production and serve frontend static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
origins = [
    "http://localhost:5173",  # React dev server
    "http://localhost:3000",  # Alternative React port
    "https://your-app-name.vercel.app",  # Replace with your Vercel URL
    "https://your-app-name.herokuapp.com",  # Replace with your Heroku URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"] if os.getenv("ENVIRONMENT") == "production" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Spaced repetition algorithm
def calculate_next_review(difficulty: int, review_count: int) -> datetime:
    """Calculate next review date based on spaced repetition algorithm"""
    base_intervals = {
        1: 1,      # Hard: 1 day
        2: 2,      # Medium-hard: 2 days
        3: 4,      # Medium: 4 days
        4: 7,      # Medium-easy: 1 week
        5: 14      # Easy: 2 weeks
    }
    
    interval = base_intervals.get(difficulty, 1)
    # Increase interval based on review count (repetition factor)
    if review_count > 0:
        interval *= (1.3 ** review_count)
    
    return datetime.utcnow() + timedelta(days=int(interval))

# API Routes
@app.get("/")
def read_root():
    return {"message": "Flashcard API is running!"}

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    # Verify credentials
    if login_data.username != VALID_USERNAME or login_data.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/decks", response_model=List[DeckResponse])
def get_decks(db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    decks = db.query(Deck).all()
    result = []
    for deck in decks:
        card_count = db.query(Flashcard).filter(Flashcard.deck_id == deck.id).count()
        result.append(DeckResponse(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            created_at=deck.created_at,
            card_count=card_count
        ))
    return result

@app.post("/decks", response_model=DeckResponse)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    db_deck = Deck(name=deck.name, description=deck.description)
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return DeckResponse(
        id=db_deck.id,
        name=db_deck.name,
        description=db_deck.description,
        created_at=db_deck.created_at,
        card_count=0
    )

@app.get("/decks/{deck_id}/cards", response_model=List[FlashcardResponse])
def get_cards(deck_id: int, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    cards = db.query(Flashcard).filter(Flashcard.deck_id == deck_id).all()
    return cards

@app.post("/cards/bulk", response_model=List[FlashcardResponse])
async def create_cards_bulk(
    deck_id: int = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    Bulk upload team member cards. Filename format should be:
    'FirstName LastName - Role.jpg' or 'FirstName_LastName_Role.jpg'
    """
    # Check if deck exists
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    created_cards = []
    errors = []
    
    for image in images:
        try:
            # Validate image file
            if not image.content_type.startswith("image/"):
                errors.append(f"File {image.filename} is not an image")
                continue
            
            # Parse filename to extract name and role
            filename_without_ext = image.filename.rsplit('.', 1)[0] if '.' in image.filename else image.filename
            
            # Try different parsing patterns
            person_name = ""
            person_role = ""
            
            if ' - ' in filename_without_ext:
                # Format: "John Doe - Software Engineer"
                parts = filename_without_ext.split(' - ', 1)
                person_name = parts[0].strip()
                person_role = parts[1].strip() if len(parts) > 1 else "Team Member"
            elif '_' in filename_without_ext:
                # Format: "John_Doe_Software_Engineer" 
                parts = filename_without_ext.split('_')
                if len(parts) >= 3:
                    # Find the split point - assume last 1-3 parts are role
                    if len(parts) >= 4:
                        person_name = ' '.join(parts[:-2]).strip()
                        person_role = ' '.join(parts[-2:]).replace('_', ' ').strip()
                    else:
                        person_name = ' '.join(parts[:-1]).strip()
                        person_role = parts[-1].replace('_', ' ').strip()
                elif len(parts) == 2:
                    person_name = parts[0].replace('_', ' ').strip()
                    person_role = parts[1].replace('_', ' ').strip()
                else:
                    person_name = filename_without_ext.replace('_', ' ').strip()
                    person_role = "Team Member"
            else:
                # Fallback: use filename as name
                person_name = filename_without_ext.strip()
                person_role = "Team Member"
            
            if not person_name:
                errors.append(f"Could not parse name from filename: {image.filename}")
                continue
            
            # Generate unique filename for storage
            file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save the uploaded image
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # Create flashcard
            db_card = Flashcard(
                deck_id=deck_id,
                front="",  # Optional front text
                back="",   # Optional back text
                person_name=person_name,
                person_role=person_role,
                image_filename=unique_filename,
                next_review=datetime.utcnow()
            )
            db.add(db_card)
            created_cards.append(db_card)
            
        except Exception as e:
            errors.append(f"Error processing {image.filename}: {str(e)}")
            continue
    
    if created_cards:
        db.commit()
        for card in created_cards:
            db.refresh(card)
    
    if errors:
        # Return partial success with error details
        error_message = f"Created {len(created_cards)} cards successfully. Errors: {'; '.join(errors)}"
        if not created_cards:
            raise HTTPException(status_code=400, detail=error_message)
    
    return created_cards

@app.post("/cards", response_model=FlashcardResponse)
async def create_card(
    deck_id: int = Form(...),
    person_name: str = Form(...),
    person_role: str = Form(...),
    front: str = Form(""),
    back: str = Form(""),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    # Check if deck exists
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Validate image file
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the uploaded image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    db_card = Flashcard(
        deck_id=deck_id,
        front=front,
        back=back,
        person_name=person_name,
        person_role=person_role,
        image_filename=unique_filename,
        next_review=datetime.utcnow()  # Available for review immediately
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@app.get("/decks/{deck_id}/study", response_model=List[FlashcardResponse])
def get_cards_for_study(deck_id: int, limit: int = 10, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    """Get cards that are due for review"""
    now = datetime.utcnow()
    cards = db.query(Flashcard).filter(
        Flashcard.deck_id == deck_id,
        Flashcard.next_review <= now
    ).limit(limit).all()
    return cards

@app.post("/cards/{card_id}/review")
def review_card(card_id: int, review: ReviewResult, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Update card based on review
    card.difficulty = review.difficulty
    card.last_reviewed = datetime.utcnow()
    card.review_count += 1
    card.next_review = calculate_next_review(review.difficulty, card.review_count)
    
    db.commit()
    return {"message": "Card reviewed successfully"}

@app.delete("/cards/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    db.delete(card)
    db.commit()
    return {"message": "Card deleted successfully"}

@app.delete("/decks/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    # Delete all cards in the deck first
    db.query(Flashcard).filter(Flashcard.deck_id == deck_id).delete()
    
    # Delete the deck
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    db.delete(deck)
    db.commit()
    return {"message": "Deck deleted successfully"}

# Serve frontend in production
@app.get("/", response_class=HTMLResponse)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_frontend(path: str = ""):
    """Serve the React frontend for all non-API routes"""
    static_path = "static/index.html"
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        # Fallback for development
        return HTMLResponse("""
        <html>
            <body>
                <h1>Flashcard API is running!</h1>
                <p>Frontend not found. This is normal in development mode.</p>
                <p>Visit <a href="/docs">/docs</a> for API documentation.</p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
