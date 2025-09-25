import { useQuery } from 'react-query'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Trophy, Medal, Crown, Award, Users } from 'lucide-react'

interface LeaderboardEntry {
  rank: number
  user_id: number
  username: string
  total_score: number
  solved_count: number
  joined_at: string
}

const Leaderboard = () => {
  const { user } = useAuth()

  const { data: leaderboard, isLoading } = useQuery('leaderboard', async () => {
    const response = await api.get('/users/leaderboard')
    return response.data.leaderboard
  })

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-6 w-6 text-yellow-500" />
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />
      case 3:
        return <Medal className="h-6 w-6 text-amber-600" />
      default:
        return <Trophy className="h-5 w-5 text-gray-400" />
    }
  }


  const getUserRank = () => {
    if (!user || !leaderboard) return null
    return leaderboard.find((entry: LeaderboardEntry) => entry.user_id === user.id)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const userRank = getUserRank()

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <Trophy className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">Leaderboard</h1>
        </div>
        <p className="text-gray-600">
          See how you stack up against other cybersecurity enthusiasts
        </p>
      </div>

      {/* User's Rank (if logged in) */}
      {userRank && (
        <div className="card p-6 bg-primary-50 border-primary-200">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {getRankIcon(userRank.rank)}
              <span className="text-2xl font-bold text-primary-900">
                #{userRank.rank}
              </span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-primary-900">
                Your Ranking
              </h3>
              <div className="flex items-center space-x-6 mt-1">
                <span className="text-sm text-primary-700">
                  {userRank.total_score} points
                </span>
                <span className="text-sm text-primary-700">
                  {userRank.solved_count} challenges solved
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Top Players
            </h2>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Users className="h-4 w-4" />
              <span>{leaderboard?.length || 0} players</span>
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {leaderboard?.map((entry: LeaderboardEntry) => (
            <div
              key={entry.user_id}
              className={`p-6 hover:bg-gray-50 transition-colors ${
                entry.user_id === user?.id ? 'bg-primary-50' : ''
              }`}
            >
              <div className="flex items-center space-x-4">
                {/* Rank */}
                <div className="flex items-center space-x-2">
                  {getRankIcon(entry.rank)}
                  <span className="text-lg font-bold text-gray-900">
                    {entry.rank}
                  </span>
                </div>

                {/* User Info */}
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {entry.username}
                    </h3>
                    {entry.user_id === user?.id && (
                      <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full">
                        You
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                    <span>Joined {new Date(entry.joined_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Stats */}
                <div className="text-right">
                  <div className="flex items-center space-x-1 mb-1">
                    <Trophy className="h-4 w-4 text-primary-600" />
                    <span className="text-xl font-bold text-gray-900">
                      {entry.total_score}
                    </span>
                    <span className="text-sm text-gray-500">pts</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {entry.solved_count} challenges solved
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {(!leaderboard || leaderboard.length === 0) && (
        <div className="text-center py-12">
          <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No rankings yet
          </h3>
          <p className="text-gray-600">
            Be the first to solve challenges and appear on the leaderboard!
          </p>
        </div>
      )}

      {/* Stats */}
      {leaderboard && leaderboard.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card p-6 text-center">
            <Award className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <h3 className="text-lg font-semibold text-gray-900">Highest Score</h3>
            <p className="text-2xl font-bold text-primary-600">
              {leaderboard[0]?.total_score || 0}
            </p>
            <p className="text-sm text-gray-500">
              by {leaderboard[0]?.username}
            </p>
          </div>

          <div className="card p-6 text-center">
            <Trophy className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <h3 className="text-lg font-semibold text-gray-900">Total Players</h3>
            <p className="text-2xl font-bold text-primary-600">
              {leaderboard.length}
            </p>
            <p className="text-sm text-gray-500">
              competing players
            </p>
          </div>

          <div className="card p-6 text-center">
            <Medal className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <h3 className="text-lg font-semibold text-gray-900">Total Solves</h3>
            <p className="text-2xl font-bold text-primary-600">
              {leaderboard.reduce((sum: number, entry: LeaderboardEntry) => sum + entry.solved_count, 0)}
            </p>
            <p className="text-sm text-gray-500">
              challenges completed
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Leaderboard
