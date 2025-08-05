import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import './StudySession.css'

interface Flashcard {
  id: number
  front: string
  back: string
  person_name: string
  person_role: string
  image_filename: string
  difficulty: number
  review_count: number
}

const StudySession = () => {
  const { deckId } = useParams<{ deckId: string }>()
  const navigate = useNavigate()
  
  const [cards, setCards] = useState<Flashcard[]>([])
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sessionComplete, setSessionComplete] = useState(false)
  const [reviewedCards, setReviewedCards] = useState(0)

  useEffect(() => {
    if (deckId) {
      fetchCards()
    }
  }, [deckId])

  const fetchCards = async () => {
    try {
      const response = await axios.get(`http://localhost:8001/decks/${deckId}/study`)
      const cardsData = response.data as Flashcard[]
      
      if (cardsData.length === 0) {
        setSessionComplete(true)
      } else {
        setCards(cardsData)
      }
    } catch (err) {
      setError('Failed to fetch cards')
      console.error('Error fetching cards:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCardFlip = () => {
    setIsFlipped(!isFlipped)
  }

  const handleReview = async (difficulty: number) => {
    const currentCard = cards[currentCardIndex]
    
    try {
      await axios.post(`http://localhost:8001/cards/${currentCard.id}/review`, {
        card_id: currentCard.id,
        difficulty: difficulty
      })

      const newReviewedCards = reviewedCards + 1
      setReviewedCards(newReviewedCards)

      if (currentCardIndex < cards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1)
        setIsFlipped(false)
      } else {
        setSessionComplete(true)
      }
    } catch (err) {
      console.error('Error reviewing card:', err)
    }
  }

  const restartSession = () => {
    setCurrentCardIndex(0)
    setIsFlipped(false)
    setSessionComplete(false)
    setReviewedCards(0)
    fetchCards()
  }

  if (loading) {
    return (
      <div className="study-container">
        <div className="loading">Loading study session...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="study-container">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/')} className="back-button">
          Back to Teams
        </button>
      </div>
    )
  }

  if (sessionComplete) {
    return (
      <div className="study-container">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="session-complete"
        >
          <div className="completion-icon">🎉</div>
          <h2>Great job!</h2>
          <p>
            {reviewedCards > 0 
              ? `You've practiced ${reviewedCards} team member${reviewedCards > 1 ? 's' : ''} in this session.`
              : 'No team members are due for review right now.'
            }
          </p>
          <div className="completion-actions">
            <button onClick={restartSession} className="restart-button">
              Practice More Team Members
            </button>
            <button onClick={() => navigate('/')} className="back-button">
              Back to Teams
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  const currentCard = cards[currentCardIndex]
  const progress = ((currentCardIndex + 1) / cards.length) * 100

  return (
    <div className="study-container">
      <div className="study-header">
        <button onClick={() => navigate('/')} className="back-link">
          ← Back to Teams
        </button>
        <div className="progress-info">
          <span>Team Member {currentCardIndex + 1} of {cards.length}</span>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      <div className="flashcard-container">
        <motion.div
          key={currentCard.id}
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -300, opacity: 0 }}
          transition={{ type: "spring", stiffness: 260, damping: 20 }}
          className="flashcard-wrapper"
        >
          <div 
            className={`flashcard ${isFlipped ? 'flipped' : ''}`}
            onClick={handleCardFlip}
          >
            <div className="flashcard-front">
              <div className="card-label">Who is this person?</div>
              <div className="card-image">
                <img 
                  src={`http://localhost:8001/uploads/${currentCard.image_filename}`}
                  alt="Team member"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/api/placeholder/300/300'
                  }}
                />
              </div>
              {currentCard.front && (
                <div className="card-additional-info">
                  {currentCard.front}
                </div>
              )}
              <div className="flip-hint">Click to reveal answer</div>
            </div>
            <div className="flashcard-back">
              <div className="card-label">Team Member</div>
              <div className="card-content">
                <div className="person-info">
                  <h3 className="person-name">{currentCard.person_name}</h3>
                  <p className="person-role">{currentCard.person_role}</p>
                  {currentCard.back && (
                    <div className="person-notes">
                      {currentCard.back}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <AnimatePresence>
          {isFlipped && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="review-buttons"
            >
              <p>How well did you know this?</p>
              <div className="difficulty-buttons">
                <button 
                  onClick={() => handleReview(1)}
                  className="difficulty-button hard"
                >
                  😰 Hard
                </button>
                <button 
                  onClick={() => handleReview(2)}
                  className="difficulty-button medium-hard"
                >
                  😕 Medium-Hard
                </button>
                <button 
                  onClick={() => handleReview(3)}
                  className="difficulty-button medium"
                >
                  😐 Medium
                </button>
                <button 
                  onClick={() => handleReview(4)}
                  className="difficulty-button medium-easy"
                >
                  🙂 Medium-Easy
                </button>
                <button 
                  onClick={() => handleReview(5)}
                  className="difficulty-button easy"
                >
                  😊 Easy
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default StudySession
