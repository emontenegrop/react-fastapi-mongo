import React, { useState, useEffect } from "react";
import {
  Eye,
  EyeOff,
  User,
  Lock,
  Mail,
  Shield,
  Menu,
  X,
  Home,
  Users,
  Settings,
  BarChart,
  FileText,
  LogOut,
} from "lucide-react";

const App = () => {
  const [currentView, setCurrentView] = useState("login");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState({
    username: "",
    password: "",
    showPassword: false,
  });

  // Password recovery state
  const [recoveryData, setRecoveryData] = useState({
    email: "",
    isLoading: false,
    message: "",
    messageType: "",
  });

  // Loading states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Función para encriptar (en producción usar una librería robusta)
  const simpleEncrypt = (text) => {
    return btoa(text); // Base64 encoding para demostración
  };

  // Función para validar email
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Función para generar código de autorización
  const generateAuthCode = () => {
    return (
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  };

  // Simular llamada a API para login
  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      // Encriptar credenciales
      const encryptedUsername = simpleEncrypt(loginData.username);
      const encryptedPassword = simpleEncrypt(loginData.password);

      // Simular llamada a API
      const response = await simulateApiCall(
        `/api/v1/usuarios/${encryptedUsername}/${encryptedPassword}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
        }
      );

      if (response.success) {
        setUserRole(response.role);
        setIsAuthenticated(true);

        // Obtener menú basado en rol
        const menuResponse = await simulateApiCall(
          `/api/v1/menus/${response.role}`
        );
        setMenuItems(menuResponse.menuItems);
      } else {
        setError("Credenciales inválidas");
      }
    } catch (err) {
      setError("Error de conexión. Intente nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  // Simular llamada a API para recuperación de contraseña
  const handlePasswordRecovery = async (e) => {
    e.preventDefault();

    if (!validateEmail(recoveryData.email)) {
      setRecoveryData((prev) => ({
        ...prev,
        message: "Por favor ingrese un email válido",
        messageType: "error",
      }));
      return;
    }

    setRecoveryData((prev) => ({ ...prev, isLoading: true }));

    try {
      const authCode = generateAuthCode();
      const expirationTime = new Date(Date.now() + 5 * 60 * 1000); // 5 minutos

      // Simular validación de email y envío
      const response = await simulateApiCall("/api/v1/password-recovery", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: recoveryData.email,
          authCode: authCode,
          expiration: expirationTime,
        }),
      });

      if (response.success) {
        setRecoveryData((prev) => ({
          ...prev,
          message: `Código de recuperación enviado a ${recoveryData.email}. Código: ${authCode} (Válido por 5 minutos)`,
          messageType: "success",
        }));
      } else {
        setRecoveryData((prev) => ({
          ...prev,
          message: "Email no encontrado en el sistema",
          messageType: "error",
        }));
      }
    } catch (err) {
      setRecoveryData((prev) => ({
        ...prev,
        message: "Error al enviar el código de recuperación",
        messageType: "error",
      }));
    } finally {
      setRecoveryData((prev) => ({ ...prev, isLoading: false }));
    }
  };

  // Simular llamadas a API
  const simulateApiCall = (url, options = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simular diferentes respuestas basadas en la URL
        if (url.includes("/api/v1/usuarios/")) {
          // Simular usuarios válidos
          const validUsers = {
            "YWRtaW4=": { password: "MTIzNDU2", role: "administrador" }, // admin:123456
            "dXNlcg==": { password: "cGFzc3dvcmQ=", role: "usuario" }, // user:password
          };

          const urlParts = url.split("/");
          const username = urlParts[urlParts.length - 2];
          const password = urlParts[urlParts.length - 1];

          const user = validUsers[username];
          if (user && user.password === password) {
            resolve({ success: true, role: user.role });
          } else {
            resolve({ success: false });
          }
        } else if (url.includes("/api/v1/menus/")) {
          const role = url.split("/").pop();
          if (role === "administrador") {
            resolve({
              menuItems: [
                { icon: "Home", label: "Dashboard", path: "/dashboard" },
                { icon: "Users", label: "Usuarios", path: "/users" },
                { icon: "Settings", label: "Configuración", path: "/settings" },
                { icon: "BarChart", label: "Reportes", path: "/reports" },
                { icon: "Shield", label: "Seguridad", path: "/security" },
              ],
            });
          } else {
            resolve({
              menuItems: [
                { icon: "Home", label: "Inicio", path: "/home" },
                { icon: "User", label: "Mi Perfil", path: "/profile" },
                {
                  icon: "FileText",
                  label: "Mis Documentos",
                  path: "/documents",
                },
              ],
            });
          }
        } else if (url.includes("/password-recovery")) {
          // Simular emails válidos
          const validEmails = [
            "admin@empresa.com",
            "user@empresa.com",
            "test@test.com",
          ];
          const email = JSON.parse(options.body).email;
          resolve({ success: validEmails.includes(email) });
        }
      }, 1500);
    });
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole(null);
    setMenuItems([]);
    setLoginData({ username: "", password: "", showPassword: false });
    setCurrentView("login");
  };

  const getIconComponent = (iconName) => {
    const icons = { Home, Users, Settings, BarChart, FileText, Shield, User };
    return icons[iconName] || Home;
  };

  // Componente de Login
  const LoginForm = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Iniciar Sesión</h1>
          <p className="text-gray-600 mt-2">
            Accede a tu cuenta de forma segura
          </p>
        </div>

        <div onSubmit={handleLogin} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Usuario
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={loginData.username}
                onChange={(e) =>
                  setLoginData((prev) => ({
                    ...prev,
                    username: e.target.value,
                  }))
                }
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Ingrese su usuario"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type={loginData.showPassword ? "text" : "password"}
                value={loginData.password}
                onChange={(e) =>
                  setLoginData((prev) => ({
                    ...prev,
                    password: e.target.value,
                  }))
                }
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Ingrese su contraseña"
                required
              />
              <button
                type="button"
                onClick={() =>
                  setLoginData((prev) => ({
                    ...prev,
                    showPassword: !prev.showPassword,
                  }))
                }
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
              >
                {loginData.showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Ingresando..." : "Ingresar"}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setCurrentView("recovery")}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>Usuarios de prueba:</p>
          <p>
            <strong>admin</strong> / 123456 (Administrador)
          </p>
          <p>
            <strong>user</strong> / password (Usuario)
          </p>
        </div>
      </div>
    </div>
  );

  // Componente de Recuperación de Contraseña
  const PasswordRecovery = () => (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Recuperar Contraseña
          </h1>
          <p className="text-gray-600 mt-2">
            Ingresa tu email para recibir un código de recuperación
          </p>
        </div>

        <div onSubmit={handlePasswordRecovery} className="space-y-6">
          {recoveryData.message && (
            <div
              className={`px-4 py-3 rounded-lg border ${
                recoveryData.messageType === "success"
                  ? "bg-green-50 border-green-200 text-green-700"
                  : "bg-red-50 border-red-200 text-red-700"
              }`}
            >
              {recoveryData.message}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={recoveryData.email}
                onChange={(e) =>
                  setRecoveryData((prev) => ({
                    ...prev,
                    email: e.target.value,
                  }))
                }
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="ejemplo@correo.com"
                required
              />
            </div>
          </div>

          <button
            type="button"
            onClick={handlePasswordRecovery}
            disabled={recoveryData.isLoading}
            className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {recoveryData.isLoading ? "Enviando..." : "Enviar Código"}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setCurrentView("login")}
              className="text-purple-600 hover:text-purple-700 text-sm font-medium"
            >
              ← Volver al login
            </button>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>Emails de prueba:</p>
          <p>admin@empresa.com, user@empresa.com, test@test.com</p>
        </div>
      </div>
    </div>
  );

  // Componente Principal de la Aplicación
  const MainApp = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="w-6 h-6 text-gray-600" />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">
              Sistema de Gestión
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Bienvenido,{" "}
              <span className="font-medium capitalize">{userRole}</span>
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Salir</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={`${
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
          } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
        >
          <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 lg:hidden">
            <span className="text-xl font-semibold text-gray-900">Menú</span>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>
          </div>

          <nav className="mt-4 px-4">
            <ul className="space-y-2">
              {menuItems.map((item, index) => {
                const IconComponent = getIconComponent(item.icon);
                return (
                  <li key={index}>
                    <a
                      href={item.path}
                      className="flex items-center space-x-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors"
                    >
                      <IconComponent className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </a>
                  </li>
                );
              })}
            </ul>
          </nav>
        </aside>

        {/* Overlay para móvil */}
        {isSidebarOpen && isMobile && (
          <div
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Contenido Principal */}
        <main className="flex-1 p-6">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Dashboard - Rol: {userRole}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {menuItems.map((item, index) => {
                const IconComponent = getIconComponent(item.icon);
                return (
                  <div
                    key={index}
                    className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-xl"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="p-3 bg-blue-600 rounded-lg">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {item.label}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Acceso disponible
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-8 p-6 bg-gray-50 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Información del Sistema
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Usuario:</span>
                  <span className="ml-2 text-gray-600">
                    {loginData.username}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Rol:</span>
                  <span className="ml-2 text-gray-600 capitalize">
                    {userRole}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">
                    Sesión iniciada:
                  </span>
                  <span className="ml-2 text-gray-600">
                    {new Date().toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Permisos:</span>
                  <span className="ml-2 text-gray-600">
                    {menuItems.length} módulos disponibles
                  </span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="text-center text-sm text-gray-600">
          © 2025 Sistema de Gestión Seguro. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  );

  // Renderizado principal
  if (isAuthenticated) {
    return <MainApp />;
  }

  return currentView === "login" ? <LoginForm /> : <PasswordRecovery />;
};

export default App;
