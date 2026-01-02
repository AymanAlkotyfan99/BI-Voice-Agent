import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import { 
  BarChart3, 
  TrendingUp,
  AlertCircle,
  Loader,
  RefreshCw
} from 'lucide-react'

import { voiceReportsAPI } from '../../api/endpoints'
import AnimatedPage from '../../components/AnimatedPage'
import Card from '../../components/Card'
import Button from '../../components/Button'
import { fadeIn, slideInBottom } from '../../animations/variants'

function DashboardViewer() {
  const [dashboardUrl, setDashboardUrl] = useState(null)
  const [reports, setReports] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
    loadReports()
  }, [])

  const loadDashboard = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await voiceReportsAPI.getWorkspaceDashboard()
      
      if (response.data.success) {
        setDashboardUrl(response.data.dashboard_url)
      } else {
        setError(response.data.error || 'Failed to load dashboard')
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error)
      
      if (error.response?.status === 404) {
        setError('No dashboard available yet. Ask your manager to create some reports first.')
      } else {
        setError(error.response?.data?.error || 'Failed to load dashboard')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const loadReports = async () => {
    try {
      const response = await voiceReportsAPI.listReports()
      
      if (response.data.success) {
        const completedReports = (response.data.reports || []).filter(r => r.status === 'completed')
        setReports(completedReports)
      }
    } catch (error) {
      console.error('Failed to load reports:', error)
    }
  }

  const handleRefresh = () => {
    loadDashboard()
    loadReports()
  }

  return (
    <AnimatedPage>
      <div className="space-y-6">
        {/* Header */}
        <motion.div variants={fadeIn}>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                📊 Analytics Dashboard
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                View workspace analytics and voice-generated reports
              </p>
            </div>

            <Button
              onClick={handleRefresh}
              variant="secondary"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <RefreshCw className="w-5 h-5 mr-2" />
                  Refresh
                </>
              )}
            </Button>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div variants={slideInBottom} className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Reports</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {reports.length}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {reports.filter(r => r.status === 'completed').length}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Rows</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {reports.reduce((sum, r) => sum + (r.row_count || 0), 0).toLocaleString()}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Dashboard */}
        <motion.div variants={slideInBottom}>
          <Card>
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader className="w-12 h-12 text-blue-600 animate-spin mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="p-4 bg-yellow-100 dark:bg-yellow-900/30 rounded-full mb-4">
                  <AlertCircle className="w-12 h-12 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Dashboard Not Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
                  {error}
                </p>
                <Button onClick={handleRefresh} className="mt-6">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
              </div>
            ) : dashboardUrl ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Workspace Analytics
                  </h2>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    Read-only view
                  </span>
                </div>
                
                <div className="border-2 border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                  <iframe
                    src={dashboardUrl}
                    width="100%"
                    height="800"
                    frameBorder="0"
                    className="bg-white"
                    title="Analytics Dashboard"
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-20">
                <BarChart3 className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Dashboard Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Ask your manager to create voice reports to see analytics here
                </p>
              </div>
            )}
          </Card>
        </motion.div>

        {/* Recent Reports */}
        {reports.length > 0 && (
          <motion.div variants={slideInBottom}>
            <Card>
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Recent Reports
              </h2>

              <div className="space-y-3">
                {reports.slice(0, 5).map((report) => (
                  <div
                    key={report.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          Report #{report.id}
                        </h3>
                        <span className="px-2 py-1 text-xs rounded-full font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                          {report.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                        {report.transcription}
                      </p>
                      {report.row_count && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {report.row_count.toLocaleString()} rows • {report.chart_type} chart
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}
      </div>
    </AnimatedPage>
  )
}

export default DashboardViewer

