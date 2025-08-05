import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import './Navigation.css'

interface NavigationProps {
  onLogout?: () => void
}

const Navigation: React.FC<NavigationProps> = ({ onLogout }) => {
  return (
    <motion.nav
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="navigation"
    >
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          🎓 Team Flashcards
        </Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">
            My Teams
          </Link>
          <Link to="/create" className="nav-link">
            + Add Team
          </Link>
          <Link to="/bulk-upload" className="nav-link nav-button">
            📤 Bulk Upload
          </Link>
          {onLogout && (
            <button onClick={onLogout} className="nav-link logout-button">
              🚪 Logout
            </button>
          )}
        </div>
      </div>
    </motion.nav>
  )
}

export default Navigation
