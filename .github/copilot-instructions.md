<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Flashcard App - Copilot Instructions

This is a full-stack flashcard application with the following architecture:

## Frontend (React + TypeScript + Vite)
- Located in `/frontend` directory
- Uses React Router for navigation
- Framer Motion for animations
- Axios for API calls
- CSS modules for styling

## Backend (Python + FastAPI)
- Located in `/backend` directory  
- FastAPI for REST API
- SQLAlchemy for database ORM
- SQLite database
- Spaced repetition algorithm for optimal learning

## Key Features
- Create and manage flashcard decks
- Interactive card flipping with animations
- Spaced repetition algorithm based on user difficulty ratings
- Progress tracking and review scheduling
- Responsive design for mobile and desktop

## API Endpoints
- GET /decks - List all decks
- POST /decks - Create new deck
- GET /decks/{id}/cards - Get cards in deck
- POST /cards - Create new card
- GET /decks/{id}/study - Get cards due for review
- POST /cards/{id}/review - Record review result
- DELETE /decks/{id} - Delete deck
- DELETE /cards/{id} - Delete card

## Database Models
- Deck: id, name, description, created_at
- Flashcard: id, deck_id, front, back, difficulty, last_reviewed, next_review, review_count

## Development Commands
- Frontend: `npm run dev` (runs on port 5173)
- Backend: `uvicorn main:app --reload` (runs on port 8000)

## Best Practices
- Use TypeScript for type safety
- Follow React hooks patterns
- Maintain consistent CSS styling
- Handle loading states and errors
- Use meaningful variable names
- Add proper error handling
