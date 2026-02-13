import { Link, useLocation } from 'react-router-dom';
import { Settings, FileText } from 'lucide-react';
import { motion } from 'framer-motion';
import { ThemeToggle } from '../ui/ThemeToggle';

export function Header() {
  const location = useLocation();
  const isAdmin = location.pathname === '/admin';
  const isQuotes = location.pathname.startsWith('/quotes');

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">IG</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 leading-tight">Island Glass</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 leading-tight">Price Calculator</p>
            </div>
          </Link>

          <div className="flex items-center gap-1">
            <ThemeToggle />
            <Link
              to="/quotes"
              className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <motion.div whileTap={{ scale: 0.9 }}>
                <FileText
                  className={`w-5 h-5 transition-colors ${
                    isQuotes ? 'text-primary-600' : 'text-gray-500'
                  }`}
                />
              </motion.div>
            </Link>
            <Link
              to={isAdmin ? '/' : '/admin'}
              className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <motion.div whileTap={{ scale: 0.9 }}>
                <Settings
                  className={`w-5 h-5 transition-colors ${
                    isAdmin ? 'text-primary-600' : 'text-gray-500'
                  }`}
                />
              </motion.div>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
