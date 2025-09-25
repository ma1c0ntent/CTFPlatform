import { useState } from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Target, Filter, Search, Trophy, Lock } from 'lucide-react'

interface Challenge {
  id: number
  title: string
  description: string
  points: number
  difficulty: string
  category_name: string
  solved?: boolean
}

const Challenges = () => {
  const [filters, setFilters] = useState({
    category: '',
    difficulty: '',
    search: ''
  })

  const { data: challenges, isLoading } = useQuery('challenges', async () => {
    const response = await api.get('/challenges')
    return response.data.challenges
  })

  const { data: categories } = useQuery('categories', async () => {
    const response = await api.get('/challenges/categories')
    return response.data.categories
  })

  const filteredChallenges = challenges?.filter((challenge: Challenge) => {
    const matchesCategory = !filters.category || challenge.category_name === filters.category
    const matchesDifficulty = !filters.difficulty || challenge.difficulty === filters.difficulty
    const matchesSearch = !filters.search || 
      challenge.title.toLowerCase().includes(filters.search.toLowerCase()) ||
      challenge.description.toLowerCase().includes(filters.search.toLowerCase())
    
    return matchesCategory && matchesDifficulty && matchesSearch
  }) || []

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Challenges</h1>
        <div className="flex items-center space-x-2">
          <Trophy className="h-5 w-5 text-primary-600" />
          <span className="text-sm text-gray-600">
            {filteredChallenges.length} challenges available
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        </div>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="input"
            >
              <option value="">All Categories</option>
              {categories?.map((category: any) => (
                <option key={category.id} value={category.name}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Difficulty
            </label>
            <select
              value={filters.difficulty}
              onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value }))}
              className="input"
            >
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search challenges..."
                className="input pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Challenges Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredChallenges.map((challenge: Challenge) => (
          <div key={challenge.id} className="card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className={`badge ${getDifficultyColor(challenge.difficulty)}`}>
                {challenge.difficulty}
              </span>
              <span className="text-sm font-medium text-gray-500">
                {challenge.points} pts
              </span>
            </div>

            <div className="flex items-center space-x-2 mb-2">
              <Target className="h-4 w-4 text-primary-600" />
              <span className="text-sm text-gray-600">{challenge.category_name}</span>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {challenge.title}
            </h3>
            
            <p className="text-gray-600 text-sm mb-4 line-clamp-3">
              {challenge.description}
            </p>

            <div className="flex items-center justify-between">
              <Link
                to={`/challenges/${challenge.id}`}
                className="btn-primary text-sm px-4 py-2"
              >
                View Challenge
              </Link>
              
              {challenge.solved && (
                <div className="flex items-center text-green-600 text-sm">
                  <Lock className="h-4 w-4 mr-1" />
                  Solved
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredChallenges.length === 0 && (
        <div className="text-center py-12">
          <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No challenges found
          </h3>
          <p className="text-gray-600">
            Try adjusting your filters to see more challenges.
          </p>
        </div>
      )}
    </div>
  )
}

export default Challenges
