import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  HomeIcon,
  BriefcaseIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  CalculatorIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Dashboard', icon: HomeIcon },
    { path: '/jobs', label: 'Jobs', icon: BriefcaseIcon },
    { path: '/schedule', label: 'Schedule', icon: CalendarIcon },
    { path: '/calculator', label: 'Calculator', icon: CalculatorIcon },
    { path: '/clients', label: 'Clients', icon: UserGroupIcon },
    { path: '/vendors', label: 'Vendors', icon: BuildingOfficeIcon },
  ];

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white flex flex-col z-40 shadow-xl">
      {/* Logo Section */}
      <div className="flex items-center h-16 px-6 bg-gray-800 flex-shrink-0">
        <h1 className="text-xl font-bold truncate">Island Glass CRM</h1>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          const indent = 'indent' in item && item.indent;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                indent ? 'ml-4' : ''
              } ${
                active
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              <span className={`${indent ? 'text-sm' : 'font-medium'}`}>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-800 p-4 flex-shrink-0">
        <div className="flex items-center px-4 py-3 bg-gray-800 rounded-lg mb-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user.email}</p>
            <p className="text-xs text-gray-400">Admin</p>
          </div>
        </div>

        {/* Admin Settings Link */}
        <Link
          to="/admin/settings"
          className={`w-full flex items-center space-x-2 px-4 py-2 mb-2 rounded-lg transition-colors ${
            isActive('/admin/settings')
              ? 'bg-blue-600 text-white'
              : 'text-gray-300 hover:bg-gray-800 hover:text-white'
          }`}
        >
          <Cog6ToothIcon className="h-5 w-5" />
          <span className="text-sm font-medium">Admin Settings</span>
        </Link>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
