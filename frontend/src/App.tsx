import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import axios from 'axios'
import DeckList from './components/DeckList'
import StudySession from './components/StudySession'
import CreateDeck from './components/CreateDeck'
import BulkUpload from './components/BulkUpload'
import Navigation from './components/Navigation'
import Login from './components/Login'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken')
    if (token) {
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setIsAuthenticated(true)
    }
    setIsLoading(false)
  }, [])

  const handleLoginSuccess = (_token: string) => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    delete axios.defaults.headers.common['Authorization']
    setIsAuthenticated(false)
  }

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">🎓</div>
        <p>Loading...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <Router>
      <div className="App">
        <Navigation onLogout={handleLogout} />
        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="main-content"
        >
          <Routes>
            <Route path="/" element={<DeckList />} />
            <Route path="/create" element={<CreateDeck />} />
            <Route path="/bulk-upload" element={<BulkUpload />} />
            <Route path="/study/:deckId" element={<StudySession />} />
          </Routes>
        </motion.main>
      </div>
    </Router>
  )
}

export default App
