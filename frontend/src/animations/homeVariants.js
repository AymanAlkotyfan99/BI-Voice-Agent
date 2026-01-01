/**
 * Animation Variants for Home Page
 * Professional, smooth animations for landing page experience
 */

// Page container animation
export const pageVariants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
}

// Navbar animation (fade down)
export const navbarVariants = {
  hidden: {
    opacity: 0,
    y: -20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
}

// Badge animation (scale + fade)
export const badgeVariants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
}

// Title slide up animation
export const titleVariants = {
  hidden: {
    opacity: 0,
    y: 30,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
}

// Subtitle fade + scale
export const subtitleVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
      delay: 0.2,
    },
  },
}

// Staggered buttons animation
export const buttonsContainerVariants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.3,
    },
  },
}

export const buttonVariants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  hover: {
    scale: 1.05,
    y: -3,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
  tap: {
    scale: 0.97,
  },
}

// Feature cards stagger container
export const cardsContainerVariants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3,
    },
  },
}

// Individual feature card animation
export const cardVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 30,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
  hover: {
    scale: 1.03,
    y: -8,
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
}

// CTA section animation
export const ctaVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
}

// Footer animation (slide up)
export const footerVariants = {
  hidden: {
    opacity: 0,
    y: 30,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
}

// Floating background elements animation
export const floatingVariants = {
  animate: {
    y: [0, -20, 0],
    x: [0, 10, 0],
    scale: [1, 1.05, 1],
    transition: {
      duration: 8,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

export const floatingVariants2 = {
  animate: {
    y: [0, 20, 0],
    x: [0, -15, 0],
    scale: [1, 1.08, 1],
    transition: {
      duration: 10,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: 1,
    },
  },
}

export const floatingVariants3 = {
  animate: {
    y: [0, -15, 0],
    x: [0, 20, 0],
    scale: [1, 1.06, 1],
    transition: {
      duration: 12,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: 2,
    },
  },
}

// Icon pulse animation
export const iconPulseVariants = {
  animate: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

// Gradient text animation
export const gradientTextVariants = {
  hidden: {
    backgroundPosition: '0% 50%',
  },
  visible: {
    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
    transition: {
      duration: 5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
}

