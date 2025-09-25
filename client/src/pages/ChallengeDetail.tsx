import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'
import { 
  ArrowLeft, 
  Clock, 
  Target, 
  Trophy, 
  CheckCircle, 
  XCircle,
  Eye,
  EyeOff
} from 'lucide-react'

const ChallengeDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()
  const [flag, setFlag] = useState('')
  const [showFlag, setShowFlag] = useState(true)
  const [multiFlags, setMultiFlags] = useState<{[key: string]: string}>({})
  const [showMultiFlags, setShowMultiFlags] = useState<{[key: string]: boolean}>({})

  const { data: challenge, isLoading } = useQuery(
    ['challenge', id],
    async () => {
      const response = await api.get(`/challenges/${id}`)
      return response.data.challenge
    },
    { enabled: !!id }
  )

  // Initialize showMultiFlags when challenge loads
  useEffect(() => {
    if (challenge?.multi_flags) {
      try {
        const multiFlagsConfig = JSON.parse(challenge.multi_flags)
        const initialShowFlags: {[key: string]: boolean} = {}
        Object.keys(multiFlagsConfig).forEach(flagKey => {
          initialShowFlags[flagKey] = true // Show by default
        })
        setShowMultiFlags(initialShowFlags)
      } catch (e) {
        console.error('Failed to parse multi_flags:', e)
      }
    }
  }, [challenge?.multi_flags])

  const submitFlagMutation = useMutation(
    async (flag: string) => {
      const response = await api.post(`/challenges/${id}/submit`, { flag })
      return response.data
    },
    {
      onSuccess: (data) => {
        if (data.correct) {
          toast.success('Correct flag! Well done!')
          queryClient.invalidateQueries(['challenge', id])
          queryClient.invalidateQueries('user-progress')
          refreshUser() // Refresh user data to update score
          setFlag('')
          // Clear multi-flags as well
          setMultiFlags({})
        } else {
          toast.error('Incorrect flag. Try again!')
        }
      },
      onError: (error: any) => {
        const message = error.response?.data?.error || 'Submission failed'
        toast.error(message)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!flag.trim()) return
    submitFlagMutation.mutate(flag.trim())
  }

  const handleMultiFlagSubmit = (flagKey: string) => {
    const flagValue = multiFlags[flagKey]
    if (!flagValue.trim()) return
    submitFlagMutation.mutate(flagValue.trim())
  }

  const updateMultiFlag = (flagKey: string, value: string) => {
    setMultiFlags(prev => ({ ...prev, [flagKey]: value }))
  }

  const toggleMultiFlagVisibility = (flagKey: string) => {
    setShowMultiFlags(prev => ({ ...prev, [flagKey]: !prev[flagKey] }))
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'badge-success'
      case 'medium': return 'badge-warning'
      case 'hard': return 'badge-danger'
      default: return 'badge-primary'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!challenge) {
    return (
      <div className="text-center py-12">
        <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Challenge not found
        </h3>
        <p className="text-gray-600 mb-4">
          The challenge you're looking for doesn't exist.
        </p>
        <button
          onClick={() => navigate('/challenges')}
          className="btn-primary"
        >
          Back to Challenges
        </button>
      </div>
    )
  }

  // Check if challenge has multi-part flags
  const hasMultiFlags = challenge.multi_flags && typeof challenge.multi_flags === 'string'
  let multiFlagsConfig = null
  if (hasMultiFlags) {
    try {
      multiFlagsConfig = JSON.parse(challenge.multi_flags)
    } catch (e) {
      console.error('Failed to parse multi_flags:', e)
    }
  }
  
  // Check if challenge is solved (all parts for multi-part, any correct for single-part)
  const isSolved = challenge.user_submissions?.some((sub: any) => sub.is_correct)
  
  // For multi-part challenges, check which parts are completed
  const completedParts = new Set()
  if (challenge.multi_flags && multiFlagsConfig) {
    challenge.user_submissions?.forEach((sub: any) => {
      if (sub.is_correct && sub.flag_type) {
        completedParts.add(sub.flag_type)
      }
    })
  }
  
  // Check if all parts are completed for multi-part challenges
  const allPartsCompleted = multiFlagsConfig ? 
    Object.keys(multiFlagsConfig).every(flagType => completedParts.has(flagType)) : 
    isSolved


  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/challenges')}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </button>
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <span className={`badge ${getDifficultyColor(challenge.difficulty)}`}>
              {challenge.difficulty}
            </span>
            <span className="text-sm text-gray-500">{challenge.category_name}</span>
            <span className="text-sm font-medium text-gray-500">
              {challenge.points} points
            </span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{challenge.title}</h1>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Challenge Description
            </h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">
                {challenge.description}
              </p>
            </div>
          </div>

          {/* Challenge Data */}
          {challenge.challenge_data && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Challenge Data
              </h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">
                  {challenge.challenge_data}
                </pre>
              </div>
            </div>
          )}

          {/* Flag Submission */}
          {user && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Submit Flag{hasMultiFlags ? 's' : ''}
              </h2>
              
              {allPartsCompleted ? (
                <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <div>
                    <h3 className="font-medium text-green-900">Challenge Solved!</h3>
                    <p className="text-sm text-green-700">
                      You've successfully solved this challenge.
                    </p>
                  </div>
                </div>
              ) : hasMultiFlags && multiFlagsConfig ? (
                // Multi-part flag submission
                <div className="space-y-6">
                  {Object.entries(multiFlagsConfig).map(([flagKey, flagValue], index) => {
                    if (typeof flagValue !== 'string') {
                      console.error('Invalid flag value for', flagKey, ':', flagValue)
                      return null
                    }
                    const isPartCompleted = completedParts.has(flagKey)
                    return (
                    <div key={flagKey} className={`border rounded-lg p-4 ${
                      isPartCompleted ? 'border-green-200 bg-green-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-medium text-gray-900">
                            Part {index + 1}: {flagKey.toUpperCase()}
                          </h3>
                          {isPartCompleted && (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          )}
                        </div>
                        <span className="text-sm text-gray-500">
                          Submit as {flagKey === 'flag2' ? 'flag2{X.X.X.X}' : `${flagKey}{answer}`}
                        </span>
                      </div>
                      
                      {isPartCompleted ? (
                        <div className="p-3 bg-green-100 rounded-lg">
                          <p className="text-sm text-green-800 font-medium">
                            ✓ {flagKey.toUpperCase()} completed successfully!
                          </p>
                        </div>
                      ) : (
                        <>
                          <div className="relative">
                            <input
                              type={showMultiFlags[flagKey] ? 'text' : 'password'}
                              value={multiFlags[flagKey] || ''}
                              onChange={(e) => updateMultiFlag(flagKey, e.target.value)}
                              placeholder={`Enter your ${flagKey} here...`}
                              className="input pr-20 w-full"
                              disabled={submitFlagMutation.isLoading}
                            />
                            <button
                              type="button"
                              onClick={() => toggleMultiFlagVisibility(flagKey)}
                              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                            >
                              {showMultiFlags[flagKey] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                          
                          <button
                            onClick={() => handleMultiFlagSubmit(flagKey)}
                            disabled={!multiFlags[flagKey]?.trim() || submitFlagMutation.isLoading}
                            className="btn-primary w-full mt-3"
                          >
                            {submitFlagMutation.isLoading ? 'Submitting...' : `Submit ${flagKey.toUpperCase()}`}
                          </button>
                        </>
                      )}
                    </div>
                    )
                  })}
                </div>
              ) : (
                // Single flag submission
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label htmlFor="flag" className="block text-sm font-medium text-gray-700 mb-2">
                      Flag
                    </label>
                    <div className="relative">
                      <input
                        id="flag"
                        type={showFlag ? 'text' : 'password'}
                        value={flag}
                        onChange={(e) => setFlag(e.target.value)}
                        placeholder="Enter your flag here..."
                        className="input pr-20"
                        disabled={submitFlagMutation.isLoading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowFlag(!showFlag)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showFlag ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={!flag.trim() || submitFlagMutation.isLoading}
                    className="btn-primary w-full"
                  >
                    {submitFlagMutation.isLoading ? 'Submitting...' : 'Submit Flag'}
                  </button>
                </form>
              )}
            </div>
          )}

          {/* Submission History */}
          {user && challenge.user_submissions && challenge.user_submissions.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Submission History
              </h2>
              <div className="space-y-3">
                {challenge.user_submissions.map((submission: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {submission.is_correct ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                      <span className="font-mono text-sm">
                        {submission.submitted_flag}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(submission.submitted_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Challenge Info */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Challenge Info
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Points</span>
                <span className="font-medium">{challenge.points}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Difficulty</span>
                <span className={`badge ${getDifficultyColor(challenge.difficulty)}`}>
                  {challenge.difficulty}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Category</span>
                <span className="text-sm font-medium">{challenge.category_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Solves</span>
                <span className="font-medium">{challenge.submission_count || 0}</span>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Your Progress
            </h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                {isSolved ? (
                  <CheckCircle className="h-6 w-6 text-green-600" />
                ) : (
                  <Clock className="h-6 w-6 text-gray-400" />
                )}
                <span className="text-sm">
                  {isSolved ? 'Solved' : 'Not solved'}
                </span>
              </div>
              
              {user && (
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Trophy className="h-4 w-4 text-primary-600" />
                    <span className="text-sm text-gray-600">
                      Your score: {user.total_score} points
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChallengeDetail
