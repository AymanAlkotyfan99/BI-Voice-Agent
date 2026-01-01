import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, BarChart3, Mic, Zap, Shield, Users, TrendingUp, Sparkles } from 'lucide-react'
import {
  pageVariants,
  navbarVariants,
  badgeVariants,
  titleVariants,
  subtitleVariants,
  buttonsContainerVariants,
  buttonVariants,
  cardsContainerVariants,
  cardVariants,
  ctaVariants,
  footerVariants,
  floatingVariants,
  floatingVariants2,
  floatingVariants3,
  iconPulseVariants,
} from '../animations/homeVariants'

function Home() {
  return (
    <motion.div
      variants={pageVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-50 relative overflow-hidden"
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          variants={floatingVariants}
          animate="animate"
          className="absolute top-20 left-10 w-72 h-72 bg-primary-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        />
        <motion.div
          variants={floatingVariants2}
          animate="animate"
          className="absolute top-40 right-20 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        />
        <motion.div
          variants={floatingVariants3}
          animate="animate"
          className="absolute -bottom-20 left-1/3 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Navigation */}
        <motion.nav
          variants={navbarVariants}
          className="container mx-auto px-6 py-6"
        >
          <div className="flex items-center justify-center">
            <motion.div
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              <BarChart3 className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                BI Voice Agent
              </span>
            </motion.div>
          </div>
        </motion.nav>

        {/* Hero Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <motion.div
              variants={badgeVariants}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-100 to-blue-100 text-primary-700 px-6 py-3 rounded-full mb-8 shadow-md"
            >
              <motion.div variants={iconPulseVariants} animate="animate">
                <Zap className="w-4 h-4" />
              </motion.div>
              <span className="text-sm font-semibold">Powered by AI & Voice Recognition</span>
              <Sparkles className="w-4 h-4" />
            </motion.div>

            {/* Title */}
            <motion.h1
              variants={titleVariants}
              className="text-5xl md:text-7xl font-extrabold text-gray-900 mb-6 leading-tight"
            >
              Convert Voice Queries into{' '}
              <span className="bg-gradient-to-r from-primary-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent animate-gradient">
                Intelligent Dashboards
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={subtitleVariants}
              className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              Transform the way your team interacts with data. Simply{' '}
              <span className="font-semibold text-primary-600">speak your questions</span> and get
              instant, actionable insights through beautiful visualizations.
            </motion.p>

            {/* Action Buttons */}
            <motion.div
              variants={buttonsContainerVariants}
              className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6"
            >
              <motion.div variants={buttonVariants} whileHover="hover" whileTap="tap">
                <Link
                  to="/signup"
                  className="btn btn-primary px-10 py-5 text-lg flex items-center space-x-3 shadow-xl hover:shadow-2xl transition-all"
                >
                  <span className="font-semibold">Create Free Account</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </motion.div>
              <motion.div variants={buttonVariants} whileHover="hover" whileTap="tap">
                <Link
                  to="/login"
                  className="btn bg-white text-gray-800 hover:bg-gray-50 border-2 border-gray-200 px-10 py-5 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Sign In
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container mx-auto px-6 py-20">
          <motion.div
            variants={cardsContainerVariants}
            className="grid md:grid-cols-3 gap-8"
          >
            {/* Feature Card 1 */}
            <motion.div variants={cardVariants} whileHover="hover">
              <div className="card bg-white/80 backdrop-blur-sm border border-gray-100 h-full">
                <motion.div
                  className="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-6 shadow-md"
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <Mic className="w-7 h-7 text-primary-600" />
                </motion.div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">
                  Voice-Powered Analytics
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Ask questions naturally using your voice and get instant insights without typing
                  or clicking. Our AI understands context and intent.
                </p>
              </div>
            </motion.div>

            {/* Feature Card 2 */}
            <motion.div variants={cardVariants} whileHover="hover">
              <div className="card bg-white/80 backdrop-blur-sm border border-gray-100 h-full">
                <motion.div
                  className="w-14 h-14 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center mb-6 shadow-md"
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <TrendingUp className="w-7 h-7 text-green-600" />
                </motion.div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">
                  Real-Time Dashboards
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Visualize your data instantly with dynamic, interactive dashboards that update in
                  real-time as your data changes.
                </p>
              </div>
            </motion.div>

            {/* Feature Card 3 */}
            <motion.div variants={cardVariants} whileHover="hover">
              <div className="card bg-white/80 backdrop-blur-sm border border-gray-100 h-full">
                <motion.div
                  className="w-14 h-14 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center mb-6 shadow-md"
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <Users className="w-7 h-7 text-purple-600" />
                </motion.div>
                <h3 className="text-2xl font-bold mb-4 text-gray-900">Team Collaboration</h3>
                <p className="text-gray-600 leading-relaxed">
                  Work together seamlessly with role-based access control, workspace management,
                  and real-time collaboration features.
                </p>
              </div>
            </motion.div>
          </motion.div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-6 py-20">
          <motion.div
            variants={ctaVariants}
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.3 }}
            className="bg-gradient-to-r from-primary-600 via-blue-600 to-indigo-600 rounded-3xl p-16 text-center text-white shadow-2xl relative overflow-hidden"
          >
            {/* Background decoration */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full filter blur-3xl" />
              <div className="absolute bottom-0 left-0 w-96 h-96 bg-white rounded-full filter blur-3xl" />
            </div>

            {/* Content */}
            <div className="relative z-10">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Shield className="w-20 h-20 mx-auto mb-8 drop-shadow-lg" />
              </motion.div>
              <h2 className="text-4xl md:text-5xl font-extrabold mb-6">
                Ready to Transform Your Data Analysis?
              </h2>
              <p className="text-xl md:text-2xl text-primary-50 mb-10 max-w-3xl mx-auto leading-relaxed">
                Join teams worldwide who are using BI Voice Agent to make data-driven decisions
                faster and smarter.
              </p>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  to="/signup"
                  className="inline-flex items-center space-x-3 bg-white text-primary-600 px-10 py-5 rounded-xl font-bold text-lg hover:bg-gray-50 transition-all shadow-xl hover:shadow-2xl"
                >
                  <span>Start Free Today</span>
                  <ArrowRight className="w-6 h-6" />
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <motion.footer
          variants={footerVariants}
          className="container mx-auto px-6 py-10 border-t border-gray-200"
        >
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <BarChart3 className="w-6 h-6 text-primary-600" />
              <span className="text-lg font-bold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                BI Voice Agent
              </span>
            </div>
            <p className="text-gray-600 text-sm">
              &copy; 2025 BI Voice Agent. All rights reserved.
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Transforming data analysis through voice and AI
            </p>
          </div>
        </motion.footer>
      </div>
    </motion.div>
  )
}

export default Home
