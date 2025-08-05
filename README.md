# 📚 Flashcard Learning App

A modern, full-stack flashcard application built with React and Python that helps you learn more effectively using spaced repetition algorithms.

## ✨ Features

- **Interactive Flashcards**: Smooth card flipping animations with beautiful UI
- **Team Member Photos**: Upload photos with names and organizational roles
- **Bulk Upload**: Upload 50+ team members at once using smart filename parsing
- **Spaced Repetition**: Intelligent algorithm that schedules reviews based on your performance
- **Deck Management**: Create, organize, and manage multiple team decks
- **Progress Tracking**: Monitor your learning progress and review history
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Updates**: Instant feedback and seamless user experience

## 🛠️ Tech Stack

### Frontend
- **React** with TypeScript for type safety
- **Vite** for fast development and building
- **React Router** for navigation
- **Framer Motion** for smooth animations
- **Axios** for API communication
- **CSS3** with modern styling

### Backend
- **FastAPI** for high-performance REST API
- **SQLAlchemy** for database ORM
- **SQLite** for data storage
- **Pydantic** for data validation
- **Uvicorn** as ASGI server

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flashcard-app
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn main:app --reload --port 8001
   ```
   The API will be available at `http://localhost:8001`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

### Quick Start (Alternative)
Use the provided startup script to launch both servers:
```bash
./start.sh
```

### Stopping the Application

#### Proper Shutdown:
- **If using start script**: Press `Ctrl+C` in the terminal running `./start.sh`
- **If running manually**: Press `Ctrl+C` in each terminal window

#### Force Cleanup (if needed):
```bash
./stop.sh
```
This script will forcefully stop all flashcard app processes and free up ports.

## 📱 Mobile Access & Deployment

### Option 1: Local Network Access (Same WiFi)
When both your computer and phone are on the same WiFi network:

1. **Find your computer's IP address:**
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   # On Windows
   ipconfig | findstr IPv4
   ```

2. **Start the app with network access:**
   ```bash
   cd backend
   source ../.venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

3. **Access from your phone:**
   - Open browser on phone
   - Go to `http://YOUR-IP-ADDRESS:5173` (replace YOUR-IP-ADDRESS)

### Option 2: Cloud Deployment (Access Anywhere)

#### Deploy to Vercel (Free)
1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Build for production:**
   ```bash
   ./build-production.sh
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

#### Deploy to Heroku (Free Tier Available)
1. **Install Heroku CLI**
2. **Create Heroku app:**
   ```bash
   heroku create your-flashcard-app
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Production build"
   git push heroku main
   ```

#### Deploy with Docker (Any Cloud Provider)
1. **Build Docker image:**
   ```bash
   docker build -t flashcard-app .
   ```

2. **Run locally:**
   ```bash
   docker-compose up
   ```

3. **Deploy to cloud:**
   - Upload to Docker Hub, AWS, Google Cloud, etc.

### Option 3: ngrok (Quick Testing)
For quick testing without permanent deployment:

1. **Install ngrok:**
   ```bash
   brew install ngrok  # macOS
   # or download from ngrok.com
   ```

2. **Start your app locally:**
   ```bash
   ./start.sh
   ```

3. **Expose to internet:**
   ```bash
   ngrok http 5173
   ```

4. **Access from anywhere:**
   - Use the ngrok URL (e.g., `https://abc123.ngrok.io`)

### Production URLs
After deployment, your app will be accessible at:
- **Vercel**: `https://your-app-name.vercel.app`
- **Heroku**: `https://your-app-name.herokuapp.com`  
- **Custom Domain**: Configure DNS to point to your server

### Security Notes
- Change default CORS origins for production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Consider authentication for private team data

## 🔧 Development

### VS Code Tasks
This project includes pre-configured VS Code tasks:
- **Start Backend Server**: Runs the Python FastAPI server
- **Start Frontend Server**: Runs the React development server
- **Start Full Application**: Runs both servers simultaneously

Access tasks via `Ctrl+Shift+P` → "Tasks: Run Task"

### API Documentation
When the backend is running, visit `http://localhost:8001/docs` for interactive API documentation powered by Swagger/OpenAPI.

### Database
The SQLite database (`flashcards.db`) is created automatically in the backend directory when you first run the server.

## 📖 Usage

### Creating Team Decks

#### Individual Upload
1. Click **"+ Add Team"** in the navigation
2. Enter a deck name and description
3. Add team members one by one:
   - Enter their **full name**
   - Enter their **role/position**
   - **Upload their photo**
   - Add optional notes
4. Click **"Create Team Deck"** to save

#### Bulk Upload (Recommended for 10+ members)
1. Click **"📤 Bulk Upload"** in the navigation
2. Enter a deck name and description
3. Select multiple image files at once
4. **Filename formats supported:**
   - `John Doe - Software Engineer.jpg`
   - `Jane_Smith_Marketing_Manager.png`
   - `Bob_Wilson_Sales.jpg`
5. Preview parsed names and roles
6. Click **"Upload Team Members"**

### Studying Team Members
### Studying Team Members
1. Select a team deck from the home page
2. Click **"📖 Study"** to start a study session
3. View the team member's photo and try to recall their name
4. Click the card to reveal their name and role
5. Rate how well you knew them (Hard to Easy) to improve future reviews

### Spaced Repetition Algorithm
The app uses a spaced repetition algorithm that:
- Schedules easier cards for longer intervals
- Reviews difficult cards more frequently
- Adapts to your individual learning pace
- Optimizes long-term retention

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/decks` | Get all decks |
| POST | `/decks` | Create a new deck |
| GET | `/decks/{id}/cards` | Get cards in a deck |
| POST | `/cards` | Create a new card |
| GET | `/decks/{id}/study` | Get cards due for review |
| POST | `/cards/{id}/review` | Record review result |
| DELETE | `/decks/{id}` | Delete a deck |
| DELETE | `/cards/{id}` | Delete a card |

## 🏗️ Project Structure

```
flashcard-app/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python backend
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── flashcards.db       # SQLite database (auto-created)
└── README.md
```

## 🎨 Customization

### Adding New Features
1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Create new components in `frontend/src/components/`
3. **Database**: Modify models in the SQLAlchemy section

### Styling
- Global styles: `frontend/src/App.css`
- Component styles: Individual `.css` files for each component

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Spaced repetition algorithm inspired by research in cognitive psychology
- UI/UX design patterns from modern learning applications
- Open source libraries that made this project possible

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Provide steps to reproduce any bugs

---

**Happy Learning! 🎓**
