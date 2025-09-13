// src/App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppStateProvider } from './contexts/AppStateContext';
import { ToastProvider } from './components/common/Toast';
import { SecurityProvider } from './components/common/SecurityProvider';
import ErrorBoundary from './components/common/ErrorBoundary';
import AppRoutes from './routes/AppRoutes';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AppStateProvider>
          <ToastProvider>
            <AuthProvider>
              <SecurityProvider>
                <div className="App">
                  <AppRoutes />
                </div>
              </SecurityProvider>
            </AuthProvider>
          </ToastProvider>
        </AppStateProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;