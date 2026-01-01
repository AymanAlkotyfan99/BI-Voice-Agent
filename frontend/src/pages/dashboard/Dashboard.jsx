import { useAuthStore } from '../../store/auth'
import { BarChart3, Users, TrendingUp, Mic, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Card, Badge, AnimatedPage } from '../../components'
import { staggerContainer, listItem, hoverLift, headerTitle, scaleFade } from '../../animations/uiVariants'

function Dashboard() {
  const { user, workspace } = useAuthStore()

  const quickActions = [
    {
      title: 'View Profile',
      description: 'Update your account information',
      icon: Users,
      link: '/dashboard/profile',
      color: 'blue',
      roles: ['manager', 'analyst', 'executive'],
    },
    {
      title: 'Workspace Settings',
      description: 'Configure your workspace',
      icon: BarChart3,
      link: '/dashboard/workspace',
      color: 'purple',
      roles: ['manager'],
    },
    {
      title: 'View Members',
      description: 'See all workspace members',
      icon: Users,
      link: '/dashboard/members',
      color: 'green',
      roles: ['manager', 'analyst', 'executive'],
    },
    {
      title: 'Invite Members',
      description: 'Add team members to workspace',
      icon: Users,
      link: '/dashboard/invite',
      color: 'orange',
      roles: ['manager'],
    },
  ]

  const filteredActions = quickActions.filter(action =>
    action.roles.includes(user?.role)
  )

  return (
    <AnimatedPage className="max-w-7xl mx-auto space-y-6">
      {/* Welcome Header */}
      <motion.div 
        variants={headerTitle}
        initial="hidden"
        animate="visible"
        className="bg-gradient-to-r from-primary-600 to-blue-600 rounded-xl p-8 text-white shadow-lg"
      >
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {user?.name}! 👋
            </h1>
            <p className="text-primary-100 text-lg">
              Ready to analyze your data with voice commands?
            </p>
          </div>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring' }}
          >
            <Badge variant="info" className="bg-white/20 text-white border-white/30">
              {user?.role}
            </Badge>
          </motion.div>
        </div>
      </motion.div>

      {/* Workspace Info */}
      {workspace && (
        <motion.div variants={scaleFade} initial="hidden" animate="visible">
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center space-x-4">
              <motion.div 
                className="w-12 h-12 bg-gradient-to-br from-primary-100 to-blue-100 rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <BarChart3 className="w-6 h-6 text-primary-600" />
              </motion.div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {workspace.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {user?.role === 'manager' ? 'Your workspace' : 'Member of this workspace'}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Quick Actions */}
      <div>
        <motion.h2 
          variants={headerTitle}
          initial="hidden"
          animate="visible"
          className="text-2xl font-bold text-gray-900 mb-4"
        >
          Quick Actions
        </motion.h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredActions.map((action, index) => {
            const Icon = action.icon
            const colorClasses = {
              blue: 'bg-blue-100 text-blue-600',
              purple: 'bg-purple-100 text-purple-600',
              green: 'bg-green-100 text-green-600',
              orange: 'bg-orange-100 text-orange-600',
            }

            return (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Link to={action.link}>
                  <Card className="hover:shadow-xl transition-shadow cursor-pointer group h-full">
                    <div className="flex items-start justify-between mb-4">
                      <div className={`w-12 h-12 ${colorClasses[action.color]} rounded-lg flex items-center justify-center`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {action.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {action.description}
                    </p>
                  </Card>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Feature Preview - Voice Analytics */}
      <motion.div variants={scaleFade} initial="hidden" animate="visible">
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-start space-x-6">
            <motion.div 
              className="w-16 h-16 bg-gradient-to-br from-primary-100 to-blue-100 rounded-xl flex items-center justify-center flex-shrink-0"
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.6 }}
            >
              <Mic className="w-8 h-8 text-primary-600" />
            </motion.div>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-xl font-semibold text-gray-900">
                  Voice Analytics (Coming Soon)
                </h3>
                <Badge variant="info">Sprint 2</Badge>
              </div>
              <p className="text-gray-600 mb-4">
                Soon you'll be able to ask questions using your voice and get instant insights 
                through beautiful, interactive dashboards. Our AI-powered voice agent will 
                understand your queries and generate the perfect visualizations.
              </p>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <TrendingUp className="w-4 h-4" />
                  <span>Real-time Analytics</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Mic className="w-4 h-4" />
                  <span>Voice Commands</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <BarChart3 className="w-4 h-4" />
                  <span>Smart Dashboards</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="grid md:grid-cols-3 gap-6"
      >
        <motion.div variants={listItem}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="text-center">
              <motion.div 
                className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full mb-3"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <TrendingUp className="w-6 h-6 text-green-600" />
              </motion.div>
              <p className="text-2xl font-bold text-gray-900">Active</p>
              <p className="text-sm text-gray-600">Account Status</p>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={listItem}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="text-center">
              <motion.div 
                className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full mb-3"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <Users className="w-6 h-6 text-blue-600" />
              </motion.div>
              <p className="text-2xl font-bold text-gray-900 capitalize">{user?.role}</p>
              <p className="text-sm text-gray-600">Your Role</p>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={listItem}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="text-center">
              <motion.div 
                className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full mb-3"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </motion.div>
              <p className="text-2xl font-bold text-gray-900">Sprint 1</p>
              <p className="text-sm text-gray-600">Current Phase</p>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatedPage>
  )
}

export default Dashboard

