import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

interface MobileHeaderProps {
  isMenuOpen: boolean;
  onMenuToggle: () => void;
}

export default function MobileHeader({ isMenuOpen, onMenuToggle }: MobileHeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-gray-900 text-white flex items-center px-4 z-40 lg:hidden shadow-md">
      {/* Hamburger/Close button */}
      <button
        type="button"
        onClick={onMenuToggle}
        className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors"
        aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isMenuOpen}
      >
        <span className="sr-only">{isMenuOpen ? 'Close menu' : 'Open menu'}</span>
        {isMenuOpen ? (
          <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
        ) : (
          <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
        )}
      </button>

      {/* App name */}
      <h1 className="ml-3 text-lg font-bold truncate">Island Glass CRM</h1>
    </header>
  );
}
