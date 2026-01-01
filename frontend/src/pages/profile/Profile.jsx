import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../../store/auth'
import { userAPI } from '../../api/endpoints'
import { User, Mail, Shield, AlertTriangle, Save, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, Input, Button, Badge, Modal, AnimatedPage } from '../../components'
import { useNavigate } from 'react-router-dom'
import { staggerContainer, staggerFast, listItem, scaleFade, headerTitle, badgeScale, glowHover } from '../../animations/uiVariants'

function Profile() {
  const { user, updateUser, logout } = useAuthStore()
  const navigate = useNavigate()
  
  const [profile, setProfile] = useState({
    name: '',
    email: '',
  })
  
  const [originalEmail, setOriginalEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isDeactivating, setIsDeactivating] = useState(false)
  const [showDeactivateModal, setShowDeactivateModal] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const response = await userAPI.getProfile()
      const userData = response.data
      setProfile({
        name: userData.name,
        email: userData.email,
      })
      setOriginalEmail(userData.email)
    } catch (error) {
      toast.error('Failed to load profile')
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!profile.name.trim()) {
      newErrors.name = 'Name is required'
    }
    
    if (!profile.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(profile.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value,
    })
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
    
    try {
      setIsLoading(true)
      
      // Only send changed fields
      const updateData = {}
      
      // Always include name if it changed
      if (profile.name !== user?.name) {
        updateData.name = profile.name
      }
      
      // Only include email if it actually changed
      if (profile.email !== originalEmail) {
        updateData.email = profile.email
      }
      
      // If nothing changed, show message and return
      if (Object.keys(updateData).length === 0) {
        toast.info('No changes to save')
        setIsLoading(false)
        return
      }
      
      const response = await userAPI.updateProfile(updateData)
      
      updateUser(response.data.user)
      
      if (profile.email !== originalEmail) {
        toast.success('Profile updated! Please verify your new email address.')
        setOriginalEmail(profile.email)
      } else {
        toast.success('Profile updated successfully!')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Failed to update profile'
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeactivate = async () => {
    try {
      setIsDeactivating(true)
      const refreshToken = localStorage.getItem('refresh_token')
      await userAPI.deactivateAccount(refreshToken)
      
      toast.success('Account deactivated successfully')
      setShowDeactivateModal(false)
      
      // Logout and redirect
      await logout()
      navigate('/login')
    } catch (error) {
      const errorMsg = error.response?.data?.message || 'Failed to deactivate account'
      toast.error(errorMsg)
    } finally {
      setIsDeactivating(false)
    }
  }

  return (
    <AnimatedPage className="max-w-4xl mx-auto space-y-6">
      <motion.div 
        variants={headerTitle}
        initial="hidden"
        animate="visible"
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account information</p>
        </div>
      </motion.div>

      {/* Profile Information Card */}
      <motion.div variants={scaleFade} initial="hidden" animate="visible">
        <Card title="Profile Information">
          <form onSubmit={handleSubmit}>
            <motion.div variants={staggerFast} initial="hidden" animate="visible" className="space-y-6">
              <motion.div variants={listItem}>
                <Input
                  label="Full Name"
                  icon={User}
                  name="name"
                  type="text"
                  required
                  value={profile.name}
                  onChange={handleChange}
                  error={errors.name}
                  placeholder="John Doe"
                />
              </motion.div>

              <motion.div variants={listItem}>
                <Input
                  label="Email Address"
                  icon={Mail}
                  name="email"
                  type="email"
                  required
                  value={profile.email}
                  onChange={handleChange}
                  error={errors.email}
                  placeholder="you@example.com"
                />
              </motion.div>

              <AnimatePresence>
                {profile.email !== originalEmail && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-lg p-4"
                  >
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <div className="text-sm text-yellow-800">
                        <p className="font-semibold">Email Change Notice</p>
                        <p className="mt-1">
                          If you change your email, you'll need to verify the new email address 
                          before you can log in with it.
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.div variants={listItem} className="flex items-center justify-between pt-4 border-t">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={loadProfile}
                >
                  Reset Changes
                </Button>
                <motion.div whileHover="hover" whileTap="tap" variants={glowHover}>
                  <Button
                    type="submit"
                    loading={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-5 h-5" />
                        <span>Save Changes</span>
                      </>
                    )}
                  </Button>
                </motion.div>
              </motion.div>
            </motion.div>
          </form>
        </Card>
      </motion.div>

      {/* Account Information Card */}
      <motion.div variants={scaleFade} initial="hidden" animate="visible" transition={{ delay: 0.1 }}>
        <Card title="Account Information">
          <motion.div variants={staggerContainer} initial="hidden" animate="visible" className="space-y-4">
            <motion.div variants={listItem} className="flex items-center justify-between py-3 border-b">
              <div className="flex items-center space-x-3">
                <Shield className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Role</p>
                  <p className="text-xs text-gray-500">Your account type</p>
                </div>
              </div>
              <motion.div variants={badgeScale} initial="hidden" animate="visible">
                <Badge variant={user?.role === 'manager' ? 'info' : 'success'}>
                  {user?.role}
                </Badge>
              </motion.div>
            </motion.div>

            <motion.div variants={listItem} className="flex items-center justify-between py-3 border-b">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Email Status</p>
                  <p className="text-xs text-gray-500">Verification status</p>
                </div>
              </div>
              <motion.div variants={badgeScale} initial="hidden" animate="visible">
                <Badge variant={user?.is_verified ? 'success' : 'warning'}>
                  {user?.is_verified ? 'Verified' : 'Pending'}
                </Badge>
              </motion.div>
            </motion.div>

            <motion.div variants={listItem} className="flex items-center justify-between py-3">
              <div className="flex items-center space-x-3">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Account Status</p>
                  <p className="text-xs text-gray-500">Active or suspended</p>
                </div>
              </div>
              <motion.div variants={badgeScale} initial="hidden" animate="visible">
                <Badge variant={user?.is_active ? 'success' : 'danger'}>
                  {user?.is_active ? 'Active' : 'Suspended'}
                </Badge>
              </motion.div>
            </motion.div>
          </motion.div>
        </Card>
      </motion.div>

      {/* Danger Zone Card */}
      <motion.div variants={scaleFade} initial="hidden" animate="visible" transition={{ delay: 0.2 }}>
        <Card title="Danger Zone">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-lg font-semibold text-red-900 mb-2">
                  Deactivate Account
                </h4>
                <p className="text-sm text-red-800 mb-4">
                  Once you deactivate your account, you will lose access to all workspaces 
                  and your data. This action can be reversed by contacting support.
                </p>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    variant="danger"
                    onClick={() => setShowDeactivateModal(true)}
                  >
                    <AlertTriangle className="w-5 h-5" />
                    <span>Deactivate Account</span>
                  </Button>
                </motion.div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Deactivate Confirmation Modal */}
      <Modal
        isOpen={showDeactivateModal}
        onClose={() => setShowDeactivateModal(false)}
        title="Deactivate Account"
      >
        <div className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
              <div className="text-sm text-red-800">
                <p className="font-medium mb-2">Are you absolutely sure?</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>You will lose access to all workspaces</li>
                  <li>Your dashboards and reports will be inaccessible</li>
                  <li>You will need to contact support to reactivate</li>
                </ul>
              </div>
            </div>
          </div>

          <p className="text-gray-600">
            This action will deactivate your account. To continue, click the button below.
          </p>

          <div className="flex items-center justify-end space-x-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => setShowDeactivateModal(false)}
              disabled={isDeactivating}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeactivate}
              loading={isDeactivating}
            >
              {isDeactivating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Deactivating...</span>
                </>
              ) : (
                'Yes, Deactivate Account'
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </AnimatedPage>
  )
}

export default Profile

