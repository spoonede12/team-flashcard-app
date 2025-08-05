import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import './DeckList.css'

interface Deck {
  id: number
  name: string
  description: string
  created_at: string
  card_count: number
}

const DeckList = () => {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDecks()
  }, [])

  const fetchDecks = async () => {
    try {
      const response = await axios.get('http://localhost:8001/decks')
      setDecks(response.data as Deck[])
    } catch (err) {
      setError('Failed to fetch decks')
      console.error('Error fetching decks:', err)
    } finally {
      setLoading(false)
    }
  }

  const deleteDeck = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this deck?')) return
    
    try {
      await axios.delete(`http://localhost:8001/decks/${id}`)
      setDecks(decks.filter(deck => deck.id !== id))
    } catch (err) {
      setError('Failed to delete deck')
      console.error('Error deleting deck:', err)
    }
  }

  if (loading) {
    return (
      <div className="deck-list-container">
        <div className="loading">Loading decks...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="deck-list-container">
        <div className="error">{error}</div>
        <button onClick={fetchDecks} className="retry-button">
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="deck-list-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="deck-list-header"
      >
        <h1>My Team Member Decks</h1>
        <p>Choose a deck to start learning about your team members!</p>
      </motion.div>

      {decks.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="empty-state"
        >
          <div className="empty-icon">📚</div>
          <h2>No team decks yet</h2>
          <p>Create your first team member deck to get started!</p>
          <Link to="/create" className="create-first-deck-button">
            Create Your First Team Deck
          </Link>
          <div style={{ marginTop: '1rem' }}>
            <Link to="/bulk-upload" className="bulk-upload-button">
              📤 Or Upload Multiple Photos at Once
            </Link>
          </div>
        </motion.div>
      ) : (
        <div className="decks-grid">
          {decks.map((deck, index) => (
            <motion.div
              key={deck.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="deck-card"
            >
              <div className="deck-card-header">
                <h3>{deck.name}</h3>
                <button
                  onClick={() => deleteDeck(deck.id)}
                  className="delete-button"
                  title="Delete deck"
                >
                  🗑️
                </button>
              </div>
              <p className="deck-description">{deck.description}</p>
              <div className="deck-stats">
                <span className="card-count">{deck.card_count} team members</span>
                <span className="created-date">
                  Created {new Date(deck.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="deck-actions">
                <Link to={`/study/${deck.id}`} className="study-button">
                  📖 Study
                </Link>
                <button className="edit-button" disabled>
                  ✏️ Edit
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DeckList
