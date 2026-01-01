import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { XCircle, AlertCircle, X } from 'lucide-react'

function ErrorAlert({ 
  message, 
  type = 'error', 
  onClose, 
  autoDismiss = true, 
  duration = 5000 
}) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (autoDismiss && message) {
      const timer = setTimeout(() => {
        handleClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [message, autoDismiss, duration])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => {
      if (onClose) onClose()
    }, 300)
  }

  if (!message) return null

  const variants = {
    hidden: { opacity: 0, y: -20, scale: 0.95 },
    visible: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, scale: 0.95, transition: { duration: 0.2 } }
  }

  const getStyles = () => {
    switch (type) {
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          icon: XCircle,
          iconColor: 'text-red-600'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800',
          icon: AlertCircle,
          iconColor: 'text-yellow-600'
        }
      case 'info':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'text-blue-800',
          icon: AlertCircle,
          iconColor: 'text-blue-600'
        }
      default:
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          icon: XCircle,
          iconColor: 'text-red-600'
        }
    }
  }

  const styles = getStyles()
  const Icon = styles.icon

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={variants}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className={`${styles.bg} ${styles.border} border rounded-lg p-4 shadow-md`}
        >
          <div className="flex items-start space-x-3">
            <Icon className={`w-5 h-5 ${styles.iconColor} mt-0.5 flex-shrink-0`} />
            <div className={`flex-1 ${styles.text}`}>
              <p className="text-sm font-medium">{message}</p>
            </div>
            <button
              onClick={handleClose}
              className={`${styles.text} hover:opacity-70 transition-opacity`}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default ErrorAlert

