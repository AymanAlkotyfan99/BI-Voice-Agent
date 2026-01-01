import { motion } from 'framer-motion'

function LoadingSkeleton({ type = 'text', count = 1, className = '' }) {
  const shimmer = {
    initial: { backgroundPosition: '-200% 0' },
    animate: {
      backgroundPosition: '200% 0',
      transition: {
        repeat: Infinity,
        duration: 1.5,
        ease: 'linear',
      },
    },
  }

  const renderSkeleton = () => {
    switch (type) {
      case 'text':
        return (
          <motion.div
            variants={shimmer}
            initial="initial"
            animate="animate"
            className={`h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded ${className}`}
            style={{ backgroundSize: '200% 100%' }}
          />
        )
      case 'title':
        return (
          <motion.div
            variants={shimmer}
            initial="initial"
            animate="animate"
            className={`h-8 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded ${className}`}
            style={{ backgroundSize: '200% 100%' }}
          />
        )
      case 'circle':
        return (
          <motion.div
            variants={shimmer}
            initial="initial"
            animate="animate"
            className={`w-12 h-12 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-full ${className}`}
            style={{ backgroundSize: '200% 100%' }}
          />
        )
      case 'card':
        return (
          <motion.div
            variants={shimmer}
            initial="initial"
            animate="animate"
            className={`h-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg ${className}`}
            style={{ backgroundSize: '200% 100%' }}
          />
        )
      case 'input':
        return (
          <motion.div
            variants={shimmer}
            initial="initial"
            animate="animate"
            className={`h-10 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg ${className}`}
            style={{ backgroundSize: '200% 100%' }}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index}>{renderSkeleton()}</div>
      ))}
    </div>
  )
}

export default LoadingSkeleton

