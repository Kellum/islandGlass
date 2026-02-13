import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { AppShell } from './components/layout/AppShell';
import { CalculatorForm } from './components/calculator/CalculatorForm';
import { AdminPanel } from './components/admin/AdminPanel';
import { QuotesList } from './pages/QuotesList';
import { QuoteDetail } from './pages/QuoteDetail';

function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<CalculatorForm />} />
            <Route path="/quotes" element={<QuotesList />} />
            <Route path="/quotes/:id" element={<QuoteDetail />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}

export default App;
