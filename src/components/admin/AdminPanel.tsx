import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LogOut } from 'lucide-react';
import { PinGate } from './PinGate';
import { GlassConfigTable } from './GlassConfigTable';
import { MarkupSettings } from './MarkupSettings';
import { EdgeWorkPricing } from './EdgeWorkPricing';
import { AuditLog } from './AuditLog';
import { TabBar } from '../ui/TabBar';
import { Button } from '../ui/Button';
import { ToastContainer } from '../ui/Toast';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import { useToast } from '../../hooks/useToast';

const TABS = [
  { id: 'wholesale', label: 'Wholesale Pricing' },
  { id: 'formula', label: 'Markup Formula' },
  { id: 'edgework', label: 'Edge Work' },
  { id: 'audit', label: 'Audit Log' },
];

export function AdminPanel() {
  const { isAuthenticated, isValidating, error, authenticate, logout, clearError } =
    useAdminAuth();
  const { toasts, addToast, removeToast } = useToast();
  const [activeTab, setActiveTab] = useState('wholesale');

  if (!isAuthenticated) {
    return (
      <PinGate
        onAuthenticate={async (pin) => {
          clearError();
          return authenticate(pin);
        }}
        isValidating={isValidating}
        error={error}
      />
    );
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Admin Settings</h1>
            <p className="text-sm text-gray-500">Manage pricing configuration</p>
          </div>
          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="w-4 h-4 mr-1.5" />
            Lock
          </Button>
        </div>

        <TabBar tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />

        <div className="mt-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'wholesale' && <GlassConfigTable onToast={addToast} />}
              {activeTab === 'formula' && <MarkupSettings onToast={addToast} />}
              {activeTab === 'edgework' && <EdgeWorkPricing onToast={addToast} />}
              {activeTab === 'audit' && <AuditLog onToast={addToast} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </>
  );
}
