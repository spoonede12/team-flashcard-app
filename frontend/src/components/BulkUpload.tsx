import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import './BulkUpload.css'

const BulkUpload = () => {
  const [deckName, setDeckName] = useState('')
  const [deckDescription, setDeckDescription] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewFiles, setPreviewFiles] = useState<Array<{name: string, parsedName: string, parsedRole: string}>>([])
  const navigate = useNavigate()

  const parseFilename = (filename: string) => {
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, "")
    
    let parsedName = ""
    let parsedRole = ""
    
    if (nameWithoutExt.includes(' - ')) {
      // Format: "John Doe - Software Engineer"
      const parts = nameWithoutExt.split(' - ')
      parsedName = parts[0].trim()
      parsedRole = parts[1]?.trim() || "Team Member"
    } else if (nameWithoutExt.includes('_')) {
      // Format: "John_Doe_Software_Engineer"
      const parts = nameWithoutExt.split('_')
      if (parts.length >= 3) {
        // Handle multi-word roles better
        if (parts.length >= 4) {
          parsedName = parts.slice(0, -2).join(' ')
          parsedRole = parts.slice(-2).join(' ')
        } else {
          parsedName = parts.slice(0, -1).join(' ')
          parsedRole = parts[parts.length - 1]
        }
      } else if (parts.length === 2) {
        parsedName = parts[0].replace(/_/g, ' ')
        parsedRole = parts[1].replace(/_/g, ' ')
      } else {
        parsedName = nameWithoutExt.replace(/_/g, ' ')
        parsedRole = "Team Member"
      }
    } else {
      parsedName = nameWithoutExt
      parsedRole = "Team Member"
    }
    
    return { parsedName, parsedRole }
  }

  const handleFileSelection = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    setSelectedFiles(files)
    
    if (files) {
      const previews = Array.from(files).map(file => {
        const { parsedName, parsedRole } = parseFilename(file.name)
        return {
          name: file.name,
          parsedName,
          parsedRole
        }
      })
      setPreviewFiles(previews)
    } else {
      setPreviewFiles([])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (!deckName.trim()) {
      setError('Deck name is required')
      setLoading(false)
      return
    }

    if (!selectedFiles || selectedFiles.length === 0) {
      setError('Please select at least one image file')
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

      // Prepare form data for bulk upload
      const formData = new FormData()
      formData.append('deck_id', deckId.toString())
      
      Array.from(selectedFiles).forEach(file => {
        formData.append('images', file)
      })

      // Upload all files at once
      await axios.post('http://localhost:8001/cards/bulk', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Navigate back to deck list
      navigate('/')
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError('Failed to upload team members')
      }
      console.error('Error uploading:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bulk-upload-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bulk-upload-header"
      >
        <h1>Bulk Upload Team Members</h1>
        <p>Upload multiple photos at once! Name your files like "John Doe - Software Engineer.jpg" or "Jane_Smith_Marketing_Manager.jpg"</p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="bulk-upload-form"
      >
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="deckName">Team Deck Name *</label>
          <input
            type="text"
            id="deckName"
            value={deckName}
            onChange={(e) => setDeckName(e.target.value)}
            placeholder="e.g., Engineering Team, Sales Team, All Staff..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="deckDescription">Description</label>
          <textarea
            id="deckDescription"
            value={deckDescription}
            onChange={(e) => setDeckDescription(e.target.value)}
            placeholder="Describe this team or department..."
            rows={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="images">Select Team Photos *</label>
          <input
            type="file"
            id="images"
            multiple
            accept="image/*"
            onChange={handleFileSelection}
            required
          />
          <div className="file-format-help">
            <strong>Filename formats supported:</strong>
            <ul>
              <li><code>John Doe - Software Engineer.jpg</code></li>
              <li><code>Jane_Smith_Marketing_Manager.png</code></li>
              <li><code>Bob_Wilson_Sales.jpg</code></li>
            </ul>
          </div>
        </div>

        {previewFiles.length > 0 && (
          <div className="file-preview">
            <h3>Preview ({previewFiles.length} files selected)</h3>
            <div className="preview-list">
              {previewFiles.slice(0, 10).map((file, index) => (
                <div key={index} className="preview-item">
                  <div className="file-info">
                    <strong>{file.parsedName}</strong>
                    <span className="role">{file.parsedRole}</span>
                    <span className="filename">{file.name}</span>
                  </div>
                </div>
              ))}
              {previewFiles.length > 10 && (
                <div className="preview-more">
                  ... and {previewFiles.length - 10} more files
                </div>
              )}
            </div>
          </div>
        )}

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
            className="upload-button"
            disabled={loading}
          >
            {loading ? `Uploading ${selectedFiles?.length || 0} members...` : `Upload ${selectedFiles?.length || 0} Team Members`}
          </button>
        </div>
      </motion.form>
    </div>
  )
}

export default BulkUpload
