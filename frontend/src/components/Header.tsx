import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-gray-800 text-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo/Title */}
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">Island Glass CRM</h1>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-6">
            <Link
              to="/jobs"
              className={`hover:text-blue-300 transition-colors ${
                isActive('/jobs') ? 'text-blue-300 font-semibold' : ''
              }`}
            >
              Jobs
            </Link>
            <Link
              to="/clients"
              className={`hover:text-blue-300 transition-colors ${
                isActive('/clients') ? 'text-blue-300 font-semibold' : ''
              }`}
            >
              Clients
            </Link>
            <Link
              to="/vendors"
              className={`hover:text-blue-300 transition-colors ${
                isActive('/vendors') ? 'text-blue-300 font-semibold' : ''
              }`}
            >
              Vendors
            </Link>
          </nav>

          {/* User Info & Logout */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-300">
              {user.email}
            </span>
            <button
              onClick={handleLogout}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded transition-colors text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
