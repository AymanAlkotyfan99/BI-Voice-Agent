import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../../store/auth'
import { UserPlus, Mail, Lock, User as UserIcon, Info } from 'lucide-react'
import { Button, Input, Select, ErrorAlert } from '../../components'
import {
  pageWrapperVariants,
  formContainerVariants,
  titleVariants,
  iconContainerVariants,
  formFieldsContainerVariants,
  formFieldVariants,
  submitButtonVariants,
  linksVariants,
  alertVariants,
  errorShakeVariants,
  floatingBlobVariants,
  floatingBlobVariants2,
} from '../../animations/formVariants'

function Signup() {
  const navigate = useNavigate()
  const { signup, isLoading } = useAuthStore()
  const [searchParams] = useSearchParams()
  
  // Check if signup is from invitation
  const invitationEmail = searchParams.get('email')
  const invitationRole = searchParams.get('role')
  const invitationToken = searchParams.get('token')
  const workspaceName = searchParams.get('workspace')
  const inviterName = searchParams.get('inviter')
  const isInvited = !!(invitationEmail && invitationRole && invitationToken)
  
  const [formData, setFormData] = useState({
    name: '',
    email: invitationEmail || '',
    password: '',
    role: invitationRole || 'analyst',
    invitation_token: invitationToken || ''
  })
  
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [showError, setShowError] = useState(false)
  
  // Update form data if invitation params change
  useEffect(() => {
    if (isInvited) {
      setFormData(prev => ({
        ...prev,
        email: invitationEmail,
        role: invitationRole,
        invitation_token: invitationToken
      }))
    }
  }, [invitationEmail, invitationRole, invitationToken, isInvited])
  
  // Show error animation
  useEffect(() => {
    if (apiError) {
      setShowError(true)
    }
  }, [apiError])

  const roleOptions = [
    { value: 'manager', label: 'Manager - Create and manage workspace' },
    { value: 'analyst', label: 'Analyst - Analyze data and create reports' },
    { value: 'executive', label: 'Executive - View reports and dashboards' },
  ]

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: null,
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setApiError('')
    setShowError(false)
    const result = await signup(formData)
    
    if (result.success) {
      // If from invitation, show different message
      if (isInvited) {
        navigate('/verify-email?sent=true&invited=true')
      } else {
        navigate('/verify-email?sent=true')
      }
    } else {
      setApiError(result.error || 'Registration failed. Please try again.')
      setShowError(true)
    }
  }

  return (
    <motion.div
      variants={pageWrapperVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-50 flex items-center justify-center px-6 py-12 relative overflow-hidden"
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          variants={floatingBlobVariants}
          animate="animate"
          className="absolute top-20 left-10 w-72 h-72 bg-primary-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        />
        <motion.div
          variants={floatingBlobVariants2}
          animate="animate"
          className="absolute bottom-20 right-20 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        />
      </div>

      {/* Form Container */}
      <motion.div
        variants={formContainerVariants}
        animate={showError ? errorShakeVariants.shake : {}}
        className="card max-w-md w-full relative z-10 bg-white/90 backdrop-blur-sm shadow-2xl"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            variants={iconContainerVariants}
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-100 to-blue-100 rounded-full mb-4 shadow-lg"
          >
            <UserPlus className="w-8 h-8 text-primary-600" />
          </motion.div>
          <motion.h2 variants={titleVariants} className="text-3xl font-bold text-gray-900">
            Create Account
          </motion.h2>
          <motion.p variants={titleVariants} className="mt-2 text-gray-600">
            {isInvited ? 'Complete your invitation' : 'Join BI Voice Agent today'}
          </motion.p>
        </div>

        {/* Invitation Info */}
        <AnimatePresence>
          {isInvited && workspaceName && (
            <motion.div
              variants={alertVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4"
            >
              <div className="flex items-start space-x-3">
                <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-blue-800">
                  <p className="font-semibold mb-1">You've been invited! 🎉</p>
                  <p>
                    {inviterName ? `${inviterName} has invited you` : 'You have been invited'} to join{' '}
                    <strong>{workspaceName}</strong> as{' '}
                    <strong>{invitationRole?.charAt(0).toUpperCase() + invitationRole?.slice(1)}</strong>.
                  </p>
                  <p className="mt-2 text-xs opacity-80">
                    Your email and role have been pre-filled. Just complete the form!
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Alert */}
        <AnimatePresence>
          {apiError && (
            <motion.div
              variants={alertVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="mb-6"
            >
              <ErrorAlert
                message={apiError}
                type="error"
                onClose={() => {
                  setApiError('')
                  setShowError(false)
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <motion.div variants={formFieldsContainerVariants}>
            {/* Name Field */}
            <motion.div variants={formFieldVariants}>
              <Input
                label="Full Name"
                icon={UserIcon}
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                error={errors.name}
                placeholder="John Doe"
              />
            </motion.div>

            {/* Email Field */}
            <motion.div variants={formFieldVariants}>
              <Input
                label="Email Address"
                icon={Mail}
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                placeholder="you@example.com"
                disabled={isInvited}
                className={isInvited ? 'bg-gray-100 cursor-not-allowed' : ''}
              />
            </motion.div>

            {/* Password Field */}
            <motion.div variants={formFieldVariants}>
              <Input
                label="Password"
                icon={Lock}
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                placeholder="••••••••"
              />
            </motion.div>

            {/* Role Field (if not invited) */}
            {!isInvited && (
              <motion.div variants={formFieldVariants}>
                <Select
                  label="Role"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  options={roleOptions}
                />
              </motion.div>
            )}

            {/* Submit Button */}
            <motion.div variants={submitButtonVariants} whileHover="hover" whileTap="tap" className="mt-8">
              <Button type="submit" loading={isLoading} fullWidth className="py-3 shadow-lg">
                {isLoading ? (
                  'Creating account...'
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    <span>Create Account</span>
                  </>
                )}
              </Button>
            </motion.div>
          </motion.div>
        </form>

        {/* Links */}
        <motion.div variants={linksVariants} className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold transition-colors">
              Sign In
            </Link>
          </p>
        </motion.div>

        <motion.div variants={linksVariants} className="mt-4 text-center">
          <Link to="/" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">
            ← Back to Home
          </Link>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

export default Signup
