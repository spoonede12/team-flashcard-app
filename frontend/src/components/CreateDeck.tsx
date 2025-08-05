import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import './CreateDeck.css'

const CreateDeck = () => {
  const [deckName, setDeckName] = useState('')
  const [deckDescription, setDeckDescription] = useState('')
  const [cards, setCards] = useState([{ person_name: '', person_role: '', front: '', back: '', image: null as File | null }])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const addCard = () => {
    setCards([...cards, { person_name: '', person_role: '', front: '', back: '', image: null }])
  }

  const removeCard = (index: number) => {
    if (cards.length > 1) {
      setCards(cards.filter((_, i) => i !== index))
    }
  }

  const updateCard = (index: number, field: 'person_name' | 'person_role' | 'front' | 'back' | 'image', value: string | File | null) => {
    const updatedCards = cards.map((card, i) => 
      i === index ? { ...card, [field]: value } : card
    )
    setCards(updatedCards)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Validate input
    if (!deckName.trim()) {
      setError('Deck name is required')
      setLoading(false)
      return
    }

    const validCards = cards.filter(card => 
      card.person_name.trim() && 
      card.person_role.trim() && 
      card.image !== null
    )
    if (validCards.length === 0) {
      setError('At least one complete card with name, role, and image is required')
      setLoading(false)
      return
    }

    try {
      // Create deck
      const deckResponse = await axios.post('http://localhost:8001/decks', {
        name: deckName.trim(),
        description: deckDescription.trim()
      })

      const deckId = (deckResponse.data as any).id

      // Create cards with form data
      for (const card of validCards) {
        const formData = new FormData()
        formData.append('deck_id', deckId.toString())
        formData.append('person_name', card.person_name.trim())
        formData.append('person_role', card.person_role.trim())
        formData.append('front', card.front.trim())
        formData.append('back', card.back.trim())
        if (card.image) {
          formData.append('image', card.image)
        }

        await axios.post('http://localhost:8001/cards', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      }

      // Navigate back to deck list
      navigate('/')
    } catch (err) {
      setError('Failed to create deck')
      console.error('Error creating deck:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="create-deck-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="create-deck-header"
      >
        <h1>Create New Team Deck</h1>
        <p>Add team members with their photos to help everyone learn names and roles</p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="create-deck-form"
      >
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="deckName">Deck Name *</label>
          <input
            type="text"
            id="deckName"
            value={deckName}
            onChange={(e) => setDeckName(e.target.value)}
            placeholder="Enter deck name..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="deckDescription">Description</label>
          <textarea
            id="deckDescription"
            value={deckDescription}
            onChange={(e) => setDeckDescription(e.target.value)}
            placeholder="Describe what this deck is about..."
            rows={3}
          />
        </div>

        <div className="cards-section">
          <div className="cards-header">
            <h3>Team Members</h3>
            <button
              type="button"
              onClick={addCard}
              className="add-card-button"
            >
              + Add Team Member
            </button>
          </div>

          <div className="cards-list">
            {cards.map((card, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card-editor"
              >
                <div className="card-editor-header">
                  <span className="card-number">Team Member {index + 1}</span>
                  {cards.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCard(index)}
                      className="remove-card-button"
                    >
                      Remove
                    </button>
                  )}
                </div>
                
                <div className="card-sides">
                  <div className="card-side">
                    <label>Person's Name *</label>
                    <input
                      type="text"
                      value={card.person_name}
                      onChange={(e) => updateCard(index, 'person_name', e.target.value)}
                      placeholder="Enter person's full name..."
                      required
                    />
                  </div>
                  
                  <div className="card-side">
                    <label>Role/Position *</label>
                    <input
                      type="text" 
                      value={card.person_role}
                      onChange={(e) => updateCard(index, 'person_role', e.target.value)}
                      placeholder="Enter their role in the organization..."
                      required
                    />
                  </div>

                  <div className="card-side">
                    <label>Photo *</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files?.[0] || null
                        updateCard(index, 'image', file)
                      }}
                      required
                    />
                    {card.image && (
                      <div className="image-preview">
                        <img 
                          src={URL.createObjectURL(card.image)} 
                          alt="Preview" 
                          style={{ maxWidth: '200px', maxHeight: '200px', marginTop: '10px' }}
                        />
                      </div>
                    )}
                  </div>
                  
                  <div className="card-side">
                    <label>Additional Info (Optional)</label>
                    <textarea
                      value={card.front}
                      onChange={(e) => updateCard(index, 'front', e.target.value)}
                      placeholder="Any additional information to show with the photo..."
                      rows={2}
                    />
                  </div>
                  
                  <div className="card-side">
                    <label>Notes (Optional)</label>
                    <textarea
                      value={card.back}
                      onChange={(e) => updateCard(index, 'back', e.target.value)}
                      placeholder="Additional notes about this person..."
                      rows={2}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="cancel-button"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="create-button"
            disabled={loading}
          >
            {loading ? 'Creating Team...' : 'Create Team Deck'}
          </button>
        </div>
      </motion.form>
    </div>
  )
}

export default CreateDeck
