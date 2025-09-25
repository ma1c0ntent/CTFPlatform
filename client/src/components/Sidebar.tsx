import { X, Home, Target, Trophy, User, Shield } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { clsx } from 'clsx'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const { user } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Challenges', href: '/challenges', icon: Target },
    { name: 'Leaderboard', href: '/leaderboard', icon: Trophy },
  ]

  const userNavigation = [
    { name: 'Profile', href: '/profile', icon: User },
  ]

  const adminNavigation = [
    { name: 'Admin Panel', href: '/admin', icon: Shield },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full pt-16 lg:pt-0">
          {/* Close button for mobile */}
          <button
            onClick={onClose}
            className="lg:hidden absolute top-4 right-4 p-2 rounded-md text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            <div className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => onClose()}
                    className={clsx(
                      'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                      isActive(item.href)
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                    )}
                  >
                    <Icon
                      className={clsx(
                        'mr-3 h-5 w-5',
                        isActive(item.href)
                          ? 'text-primary-500'
                          : 'text-gray-400 group-hover:text-gray-500'
                      )}
                    />
                    {item.name}
                  </Link>
                )
              })}
            </div>

            {/* User section */}
            {user && (
              <>
                <div className="pt-6">
                  <div className="border-t border-gray-200 pt-6">
                    <div className="space-y-1">
                      {userNavigation.map((item) => {
                        const Icon = item.icon
                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                            onClick={() => onClose()}
                            className={clsx(
                              'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                              isActive(item.href)
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                            )}
                          >
                            <Icon
                              className={clsx(
                                'mr-3 h-5 w-5',
                                isActive(item.href)
                                  ? 'text-primary-500'
                                  : 'text-gray-400 group-hover:text-gray-500'
                              )}
                            />
                            {item.name}
                          </Link>
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* Admin section */}
                {user.is_admin && (
                  <div className="pt-4">
                    <div className="border-t border-gray-200 pt-4">
                      <div className="space-y-1">
                        {adminNavigation.map((item) => {
                          const Icon = item.icon
                          return (
                            <Link
                              key={item.name}
                              to={item.href}
                              onClick={() => onClose()}
                              className={clsx(
                                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                                isActive(item.href)
                                  ? 'bg-primary-100 text-primary-700'
                                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                              )}
                            >
                              <Icon
                                className={clsx(
                                  'mr-3 h-5 w-5',
                                  isActive(item.href)
                                    ? 'text-primary-500'
                                    : 'text-gray-400 group-hover:text-gray-500'
                                )}
                              />
                              {item.name}
                            </Link>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </nav>
        </div>
      </div>
    </>
  )
}

export default Sidebar
