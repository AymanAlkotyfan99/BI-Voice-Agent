import { Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { buttonTap, buttonHover } from '../animations/variants'

/**
 * Animated Button Component
 * Features: Loading state, disabled state, multiple variants and sizes
 * Animation: Smooth hover and tap effects
 */
function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false,
  fullWidth = false,
  className = '',
  ...props 
}) {
  const baseStyles = 'btn inline-flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
    success: 'bg-green-600 text-white hover:bg-green-700',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  }
  
  const widthClass = fullWidth ? 'w-full' : ''
  
  return (
    <motion.button
      whileHover={disabled || loading ? {} : buttonHover}
      whileTap={disabled || loading ? {} : buttonTap}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${widthClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className="w-4 h-4" />
        </motion.div>
      )}
      {children}
    </motion.button>
  )
}

export default Button

