import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '../services/api'
import toast from 'react-hot-toast'
import { 
  Shield, 
  Users, 
  Target, 
  Trophy, 
  Plus, 
  Edit, 
  Trash2, 
  Eye,
  EyeOff,
  BarChart3
} from 'lucide-react'

const Admin = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [showHiddenChallenges, setShowHiddenChallenges] = useState(true)
  const queryClient = useQueryClient()

  const { data: stats } = useQuery('admin-stats', async () => {
    const response = await api.get('/admin/stats')
    return response.data.stats
  })

  const { data: users } = useQuery('admin-users', async () => {
    const response = await api.get('/admin/users')
    return response.data.users
  })

  const { data: challenges } = useQuery('admin-challenges', async () => {
    const response = await api.get(`/challenges?include_hidden=${showHiddenChallenges}`)
    return response.data.challenges
  }, {
    enabled: activeTab === 'challenges'
  })

  // Reset user score mutation
  const resetUserScoreMutation = useMutation(
    async (userId: number) => {
      const response = await api.post(`/admin/users/${userId}/reset-score`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(data.message)
        queryClient.invalidateQueries('admin-users')
        queryClient.invalidateQueries('admin-stats')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to reset user score')
      }
    }
  )

  // Reset challenge submissions mutation
  const resetChallengeMutation = useMutation(
    async (challengeId: number) => {
      const response = await api.post(`/admin/challenges/${challengeId}/reset`, {}, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(data.message)
        queryClient.invalidateQueries('admin-users')
        queryClient.invalidateQueries('admin-stats')
        queryClient.invalidateQueries('admin-challenges')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to reset challenge')
      }
    }
  )

  // Delete user mutation
  const deleteUserMutation = useMutation(
    async (userId: number) => {
      const response = await api.delete(`/admin/users/${userId}`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(data.message)
        queryClient.invalidateQueries('admin-users')
        queryClient.invalidateQueries('admin-stats')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to delete user')
      }
    }
  )

  // Toggle challenge visibility mutation
  const toggleChallengeVisibilityMutation = useMutation(
    async (challengeId: number) => {
      const response = await api.put(`/admin/challenges/${challengeId}/toggle-visibility`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(data.message)
        queryClient.invalidateQueries('admin-challenges')
        queryClient.invalidateQueries('admin-stats')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to toggle challenge visibility')
      }
    }
  )

  // Delete challenge mutation
  const deleteChallengeMutation = useMutation(
    async (challengeId: number) => {
      const response = await api.delete(`/admin/challenges/${challengeId}/delete`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(data.message)
        queryClient.invalidateQueries('admin-challenges')
        queryClient.invalidateQueries('admin-stats')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to delete challenge')
      }
    }
  )

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'users', name: 'Users', icon: Users },
    { id: 'challenges', name: 'Challenges', icon: Target },
  ]

  const OverviewTab = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Platform Overview</h2>
      
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Challenges</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_challenges}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <Trophy className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Solves</p>
                <p className="text-2xl font-bold text-gray-900">{stats.correct_submissions}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Admins</p>
                <p className="text-2xl font-bold text-gray-900">{stats.admin_users}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Challenge Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Active Challenges</span>
              <span className="font-medium">{stats?.active_challenges || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Hidden Challenges</span>
              <span className="font-medium">{stats?.hidden_challenges || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Categories</span>
              <span className="font-medium">{stats?.categories || 0}</span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Active Users</span>
              <span className="font-medium">{stats?.active_users || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total Submissions</span>
              <span className="font-medium">{stats?.total_submissions || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Recent Registrations</span>
              <span className="font-medium">{stats?.recent_registrations || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const UsersTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <button className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users?.map((user: any) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                          <Users className="h-5 w-5 text-primary-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {user.is_admin && (
                        <span className="badge badge-primary">Admin</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.total_score}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button 
                      className="text-primary-600 hover:text-primary-900 mr-3"
                      title="Reset User Score"
                      onClick={() => {
                        if (window.confirm(`Reset score and submissions for ${user.username}?`)) {
                          resetUserScoreMutation.mutate(user.id)
                        }
                      }}
                      disabled={resetUserScoreMutation.isLoading}
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button 
                      className="text-red-600 hover:text-red-900"
                      title="Delete User"
                      onClick={() => {
                        const confirmMessage = user.is_admin 
                          ? `⚠️ WARNING: This will delete admin user "${user.username}". Are you sure?`
                          : `Delete user "${user.username}"? This action cannot be undone.`;
                        
                        if (window.confirm(confirmMessage)) {
                          deleteUserMutation.mutate(user.id)
                        }
                      }}
                      disabled={deleteUserMutation.isLoading}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const ChallengesTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Challenge Management</h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showHiddenChallenges}
              onChange={(e) => setShowHiddenChallenges(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-600">Show Hidden Challenges</span>
          </label>
          <button className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            Add Challenge
          </button>
        </div>
      </div>

      <div className="grid gap-6">
        {challenges?.map((challenge: any) => (
          <div key={challenge.id} className="card p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {challenge.title}
                  </h3>
                  <span className={`badge ${
                    challenge.difficulty === 'Easy' ? 'badge-success' :
                    challenge.difficulty === 'Medium' ? 'badge-warning' : 'badge-danger'
                  }`}>
                    {challenge.difficulty}
                  </span>
                  <span className="text-sm text-gray-500">
                    {challenge.points} pts
                  </span>
                  {!challenge.is_active && (
                    <span className="badge badge-danger">
                      Hidden
                    </span>
                  )}
                </div>
                <p className="text-gray-600 text-sm mb-2">
                  {challenge.description}
                </p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>Category: {challenge.category_name}</span>
                  <span>Solves: {challenge.submission_count || 0}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button 
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title={challenge.is_active ? "Hide Challenge" : "Show Challenge"}
                  onClick={() => {
                    const action = challenge.is_active ? "hide" : "show";
                    if (window.confirm(`${action === "hide" ? "Hide" : "Show"} challenge "${challenge.title}"?`)) {
                      toggleChallengeVisibilityMutation.mutate(challenge.id)
                    }
                  }}
                  disabled={toggleChallengeVisibilityMutation.isLoading}
                >
                  {challenge.is_active ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </button>
                <button 
                  className="p-2 text-primary-600 hover:text-primary-900"
                  title="Reset Challenge Submissions"
                  onClick={() => {
                    if (window.confirm(`Reset all submissions for "${challenge.title}"?`)) {
                      resetChallengeMutation.mutate(challenge.id)
                    }
                  }}
                  disabled={resetChallengeMutation.isLoading}
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button 
                  className="p-2 text-red-600 hover:text-red-900"
                  title="Delete Challenge"
                  onClick={() => {
                    if (window.confirm(`⚠️ WARNING: This will permanently delete challenge "${challenge.title}" and all submissions. This action cannot be undone. Are you sure?`)) {
                      deleteChallengeMutation.mutate(challenge.id)
                    }
                  }}
                  disabled={deleteChallengeMutation.isLoading}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Shield className="h-8 w-8 text-purple-600" />
        <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'challenges' && <ChallengesTab />}
      </div>
    </div>
  )
}

export default Admin
