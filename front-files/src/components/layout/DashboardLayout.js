// src/components/layout/DashboardLayout.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSecurity } from '../common/SecurityProvider';
import Sidebar from './Sidebar';
import Header from './Header';
import { useToast } from '../common/Toast';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const { sessionManager } = useSecurity();
  const { toast } = useToast();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) {
        setIsSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Session timeout warning
  useEffect(() => {
    const checkSession = () => {
      const timeLeft = sessionManager.getTimeUntilExpiry();
      if (timeLeft > 0 && timeLeft <= 5 * 60 * 1000) { // 5 minutes warning
        toast.warning('Su sesión expirará pronto', {
          duration: 10000
        });
      }
    };

    const interval = setInterval(checkSession, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [sessionManager, toast]);

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogout = () => {
    logout();
    toast.success('Sesión cerrada correctamente');
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        isMobile={isMobile}
      />

      {/* Mobile overlay */}
      {isSidebarOpen && isMobile && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header 
          user={user}
          onSidebarToggle={handleSidebarToggle}
          onLogout={handleLogout}
          isMobile={isMobile}
        />
        
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-4 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
              <div>
                © 2025 EMTechnology. Todos los derechos reservados.
              </div>
              <div className="mt-2 sm:mt-0">
                Versión 1.0.0 | Sistema de Gestión Seguro
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default DashboardLayout;