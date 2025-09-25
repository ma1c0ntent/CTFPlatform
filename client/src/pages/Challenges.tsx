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
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Challenges</h1>
        <div className="flex items-center justify-center space-x-2">
          <Trophy className="h-5 w-5 text-primary-600" />
          <span className="text-lg text-gray-600">
            {filteredChallenges.length} challenges available
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-8 text-center">
        <div className="flex items-center justify-center space-x-4 mb-6">
          <Filter className="h-6 w-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Filters</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
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
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {filteredChallenges.map((challenge: Challenge) => (
          <div key={challenge.id} className="card p-8 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 text-center">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <span className={`badge ${getDifficultyColor(challenge.difficulty)}`}>
                {challenge.difficulty}
              </span>
              <span className="text-lg font-medium text-gray-500">
                {challenge.points} pts
              </span>
            </div>

            <div className="flex items-center justify-center space-x-2 mb-4">
              <Target className="h-5 w-5 text-primary-600" />
              <span className="text-sm text-gray-600 font-medium">{challenge.category_name}</span>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {challenge.title}
            </h3>
            
            <p className="text-gray-600 mb-6 line-clamp-3 leading-relaxed">
              {challenge.description}
            </p>

            <div className="space-y-4">
              <Link
                to={`/challenges/${challenge.id}`}
                className="btn-primary w-full text-center py-3"
              >
                View Challenge
              </Link>
              
              {challenge.solved && (
                <div className="flex items-center justify-center text-green-600 text-sm font-medium">
                  <Lock className="h-4 w-4 mr-2" />
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
