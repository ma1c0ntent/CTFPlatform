import { useQuery } from 'react-query'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Target, Trophy, Users, Zap, ArrowRight, Shield } from 'lucide-react'
import { Link } from 'react-router-dom'

const Home = () => {
  const { user } = useAuth()

  const { data: stats } = useQuery('platform-stats', async () => {
    const response = await api.get('/users/stats')
    return response.data.stats
  })

  const { data: recentChallenges } = useQuery('recent-challenges', async () => {
    const response = await api.get('/challenges?per_page=6')
    return response.data.challenges
  })

  const features = [
    {
      icon: Target,
      title: 'Interactive Challenges',
      description: 'Solve cybersecurity challenges directly in your browser without installing anything.'
    },
    {
      icon: Trophy,
      title: 'Competitive Scoring',
      description: 'Earn points for solving challenges and compete on the leaderboard.'
    },
    {
      icon: Shield,
      title: 'Safe Environment',
      description: 'All challenges run in secure, sandboxed environments.'
    },
    {
      icon: Zap,
      title: 'Real-time Progress',
      description: 'Track your progress and see your skills improve over time.'
    }
  ]

  const categories = [
    { name: 'Cryptography', color: 'bg-blue-500', description: 'Encryption, decryption, and crypto analysis' },
    { name: 'Web Security', color: 'bg-green-500', description: 'XSS, SQL injection, and web vulnerabilities' },
    { name: 'Forensics', color: 'bg-purple-500', description: 'File analysis, steganography, and data recovery' },
    { name: 'Reverse Engineering', color: 'bg-red-500', description: 'Binary analysis and code understanding' },
    { name: 'Network Security', color: 'bg-yellow-500', description: 'Packet analysis and network protocols' },
    { name: 'Miscellaneous', color: 'bg-gray-500', description: 'General security concepts and puzzles' }
  ]

  return (
    <div className="space-y-16">
      {/* Hero section */}
      <section className="text-center py-16">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-8">
          Welcome to{' '}
          <span className="text-gradient">CTF Platform</span>
        </h1>
        <p className="text-xl text-gray-600 mb-10 max-w-4xl mx-auto leading-relaxed">
          A modern web-based Capture The Flag platform for cybersecurity education. 
          Learn, practice, and compete in a safe environment.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/challenges"
            className="btn-primary text-lg px-10 py-4 inline-flex items-center justify-center"
          >
            Start Solving
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/leaderboard"
            className="btn-outline text-lg px-10 py-4"
          >
            View Leaderboard
          </Link>
        </div>
      </section>

      {/* Stats section */}
      {stats && (
        <section className="text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              <div className="card p-6 text-center">
                <Users className="h-8 w-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.total_users}</div>
                <div className="text-sm text-gray-500">Active Users</div>
              </div>
              <div className="card p-6 text-center">
                <Target className="h-8 w-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.total_challenges}</div>
                <div className="text-sm text-gray-500">Challenges</div>
              </div>
              <div className="card p-6 text-center">
                <Trophy className="h-8 w-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.total_solves}</div>
                <div className="text-sm text-gray-500">Solutions</div>
              </div>
              <div className="card p-6 text-center">
                <Shield className="h-8 w-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.total_categories || 6}</div>
                <div className="text-sm text-gray-500">Categories</div>
              </div>
            </div>
          </section>
        )}

        {/* Features section */}
        <section className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-16">
            Why Choose Our Platform?
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="card p-8 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <Icon className="h-14 w-14 text-primary-600 mx-auto mb-6" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </section>

        {/* Categories section */}
        <section className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-16">
            Challenge Categories
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {categories.map((category, index) => (
              <div key={index} className="card p-8 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-center justify-center mb-6">
                  <div className={`w-6 h-6 rounded-full ${category.color} mr-4`}></div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {category.name}
                  </h3>
                </div>
                <p className="text-gray-600 leading-relaxed text-center">
                  {category.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Recent challenges section */}
        {recentChallenges && recentChallenges.length > 0 && (
          <section className="text-center">
            <div className="flex flex-col sm:flex-row items-center justify-between mb-12 max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 mb-4 sm:mb-0">
                Recent Challenges
              </h2>
              <Link
                to="/challenges"
                className="btn-outline inline-flex items-center px-6 py-3"
              >
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {recentChallenges.map((challenge: any) => (
                <div key={challenge.id} className="card p-8 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <div className="flex items-center justify-between mb-4">
                    <span className={`badge badge-${challenge.difficulty.toLowerCase()}`}>
                      {challenge.difficulty}
                    </span>
                    <span className="text-sm font-medium text-gray-500">
                      {challenge.points} pts
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {challenge.title}
                  </h3>
                  <p className="text-gray-600 mb-6 line-clamp-2 leading-relaxed">
                    {challenge.description}
                  </p>
                  <Link
                    to={`/challenges/${challenge.id}`}
                    className="btn-primary w-full text-center py-3"
                  >
                    View Challenge
                  </Link>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* CTA section */}
        {!user && (
          <section className="bg-primary-600 rounded-2xl p-12 text-center text-white max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">
              Ready to Start Your Journey?
            </h2>
            <p className="text-xl mb-10 opacity-90 leading-relaxed">
              Join thousands of cybersecurity enthusiasts and start solving challenges today.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Link
                to="/register"
                className="bg-white text-primary-600 hover:bg-gray-100 px-10 py-4 rounded-lg font-medium inline-flex items-center justify-center text-lg transition-all duration-300 hover:scale-105"
              >
                Create Account
              </Link>
              <Link
                to="/challenges"
                className="border-2 border-white text-white hover:bg-white hover:text-primary-600 px-10 py-4 rounded-lg font-medium inline-flex items-center justify-center text-lg transition-all duration-300 hover:scale-105"
              >
                Browse Challenges
              </Link>
            </div>
          </section>
        )}
    </div>
  )
}

export default Home
