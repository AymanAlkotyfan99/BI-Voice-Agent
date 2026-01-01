import { motion } from 'framer-motion'
import { pageVariants } from '../animations/variants'

/**
 * PageWrapper Component
 * Wraps all pages with consistent fade-in animation
 * 
 * Usage:
 * <PageWrapper>
 *   <YourPageContent />
 * </PageWrapper>
 */
function PageWrapper({ children, className = '' }) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export default PageWrapper

