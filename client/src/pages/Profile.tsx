import { useQuery } from 'react-query'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { User, Trophy, Target, Calendar, Award } from 'lucide-react'

const Profile = () => {
  const { user } = useAuth()

  const { data: progress } = useQuery(
    'user-progress',
    async () => {
      const response = await api.get('/challenges/user-progress')
      return response.data.progress
    },
    { enabled: !!user }
  )

  const { data: stats } = useQuery(
    'my-stats',
    async () => {
      const response = await api.get('/users/my-stats')
      return response.data.stats
    },
    { enabled: !!user }
  )

  if (!user) {
    return (
      <div className="text-center py-12">
        <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Please log in to view your profile
        </h3>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Profile Header */}
      <div className="card p-8 text-center">
        <div className="flex flex-col items-center space-y-6">
          <div className="h-24 w-24 bg-primary-100 rounded-full flex items-center justify-center">
            <User className="h-12 w-12 text-primary-600" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{user.username}</h1>
            <p className="text-xl text-gray-600">{user.email}</p>
            <div className="flex items-center justify-center space-x-6 mt-4">
              <div className="flex items-center space-x-1">
                <Trophy className="h-4 w-4 text-primary-600" />
                <span className="text-sm font-medium">{user.total_score} points</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-500">
                  Joined {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          {user.is_admin && (
            <div className="flex items-center space-x-1 bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
              <Award className="h-4 w-4" />
              <span>Admin</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Progress Overview */}
          {progress && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Progress Overview
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-primary-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-primary-600 font-medium">Challenges Solved</p>
                      <p className="text-2xl font-bold text-primary-900">
                        {progress.solved_challenges}
                      </p>
                    </div>
                    <Target className="h-8 w-8 text-primary-600" />
                  </div>
                  <p className="text-xs text-primary-600 mt-1">
                    out of {progress.total_challenges} total
                  </p>
                </div>

                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-600 font-medium">Completion Rate</p>
                      <p className="text-2xl font-bold text-green-900">
                        {progress.completion_percentage}%
                      </p>
                    </div>
                    <Trophy className="h-8 w-8 text-green-600" />
                  </div>
                  <p className="text-xs text-green-600 mt-1">
                    challenges completed
                  </p>
                </div>
              </div>

              {/* Progress by Category */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Progress by Category
                </h3>
                <div className="space-y-3">
                  {Object.entries(progress.progress_by_category).map(([category, data]: [string, any]) => (
                    <div key={category} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700">{category}</span>
                        <span className="text-gray-500">
                          {data.solved}/{data.total} ({data.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${data.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Progress by Difficulty */}
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Progress by Difficulty
                </h3>
                <div className="space-y-3">
                  {Object.entries(progress.progress_by_difficulty).map(([difficulty, data]: [string, any]) => (
                    <div key={difficulty} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700">{difficulty}</span>
                        <span className="text-gray-500">
                          {data.solved}/{data.total} ({data.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            difficulty === 'Easy' ? 'bg-green-500' :
                            difficulty === 'Medium' ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${data.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recent Activity */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Recent Activity
            </h2>
            <div className="text-center py-8 text-gray-500">
              <Target className="h-8 w-8 mx-auto mb-2" />
              <p>Recent activity will appear here</p>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Statistics */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Statistics
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Score</span>
                <span className="font-medium">{user.total_score}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Challenges Solved</span>
                <span className="font-medium">{progress?.solved_challenges || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Completion Rate</span>
                <span className="font-medium">{progress?.completion_percentage || 0}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Account Created</span>
                <span className="font-medium">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* User Stats */}
          {stats && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Your Stats
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Total Points</span>
                  <span className="font-medium text-primary-600">{stats.total_points}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Challenges Solved</span>
                  <span className="font-medium">{stats.total_solves}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">This Month</span>
                  <span className="font-medium">{stats.recent_solves}</span>
                </div>
                {stats.rank && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Rank</span>
                    <span className="font-medium">#{stats.rank}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile
