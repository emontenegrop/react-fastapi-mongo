// src/components/layout/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Users, 
  Settings, 
  BarChart,
  Shield,
  X,
  ChevronRight
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose, isMobile }) => {
  const menuItems = [
    { 
      path: '/dashboard', 
      label: 'Dashboard', 
      icon: Home,
      description: 'Panel principal'
    },
    { 
      path: '/files', 
      label: 'Archivos', 
      icon: FileText,
      description: 'Gestión de archivos'
    },
    { 
      path: '/users', 
      label: 'Usuarios', 
      icon: Users,
      description: 'Administrar usuarios',
      requiresRole: 'administrador'
    },
    { 
      path: '/reports', 
      label: 'Reportes', 
      icon: BarChart,
      description: 'Informes y estadísticas'
    },
    { 
      path: '/security', 
      label: 'Seguridad', 
      icon: Shield,
      description: 'Configuración de seguridad',
      requiresRole: 'administrador'
    },
    { 
      path: '/settings', 
      label: 'Configuración', 
      icon: Settings,
      description: 'Preferencias del sistema'
    }
  ];

  const handleItemClick = () => {
    if (isMobile && onClose) {
      onClose();
    }
  };

  return (
    <>
      {/* Sidebar */}
      <aside
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 border-r border-gray-200`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 lg:hidden">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-gray-900">Menu</span>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {menuItems.map((item) => {
              const IconComponent = item.icon;
              
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={handleItemClick}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <IconComponent
                    className={`mr-3 h-5 w-5 flex-shrink-0 transition-colors`}
                  />
                  <div className="flex-1 min-w-0">
                    <span className="truncate">{item.label}</span>
                    {!isMobile && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">
                        {item.description}
                      </p>
                    )}
                  </div>
                  <ChevronRight className="ml-2 h-4 w-4 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </NavLink>
              );
            })}
          </div>

          {/* Section divider */}
          <div className="my-6 border-t border-gray-200"></div>

          {/* Quick Actions */}
          <div className="space-y-1">
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Accesos Rápidos
            </h3>
            
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
              + Nuevo Archivo
            </button>
            
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
              📊 Ver Estadísticas
            </button>
          </div>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                Front Files
              </p>
              <p className="text-xs text-gray-500">
                v1.0.0
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
