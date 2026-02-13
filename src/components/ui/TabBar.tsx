import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface Tab {
  id: string;
  label: string;
}

interface TabBarProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (id: string) => void;
}

export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="-mb-px flex space-x-1 overflow-x-auto px-1" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'relative py-3 px-4 text-sm font-medium whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'text-primary-600'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            )}
          >
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="admin-tab-indicator"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </nav>
    </div>
  );
}
