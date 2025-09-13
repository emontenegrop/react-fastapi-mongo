// src/pages/LoginPage.js
import { useState, useEffect } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { useAuth } from "../contexts/AuthContext";
import { validationSchemas, rateLimiter } from "../utils/validation";
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  AlertCircle,
  Loader2
} from "lucide-react";
import { Link } from "react-router-dom";

const LoginPage = () => {
  const { login, error, clearError, loading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);
  const [remainingTime, setRemainingTime] = useState(0);

  // Check rate limiting on component mount
  useEffect(() => {
    checkRateLimit();
  }, []);

  // Update remaining time for blocked users
  useEffect(() => {
    let interval;
    if (isBlocked && remainingTime > 0) {
      interval = setInterval(() => {
        const remaining = rateLimiter.getRemainingTime('login');
        setRemainingTime(remaining);
        
        if (remaining <= 0) {
          setIsBlocked(false);
          setRemainingTime(0);
        }
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isBlocked, remainingTime]);

  const checkRateLimit = () => {
    const blocked = rateLimiter.isBlocked('login');
    setIsBlocked(blocked);
    
    if (blocked) {
      const remaining = rateLimiter.getRemainingTime('login');
      setRemainingTime(remaining);
    }
  };

  const handleSubmit = async (values, { setSubmitting, setErrors, setFieldError }) => {
    try {
      // Clear any previous errors
      clearError();
      
      // Check rate limiting
      if (rateLimiter.isBlocked('login')) {
        checkRateLimit();
        setErrors({ 
          general: `Demasiados intentos fallidos. Intente nuevamente en ${Math.ceil(remainingTime / 1000 / 60)} minutos.` 
        });
        return;
      }

      // Record login attempt
      rateLimiter.recordAttempt('login');
      
      await login(values.email, values.password);
      
    } catch (error) {
      // Check if we should block further attempts
      checkRateLimit();
      
      // Set appropriate error message
      if (error.message.includes('credenciales')) {
        setFieldError('password', 'Credenciales incorrectas');
      } else if (error.message.includes('red')) {
        setErrors({ general: 'Error de conexión. Verifique su internet.' });
      } else {
        setErrors({ general: error.message });
      }
    } finally {
      setSubmitting(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const formatTime = (ms) => {
    const minutes = Math.floor(ms / 1000 / 60);
    const seconds = Math.floor((ms / 1000) % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Iniciar Sesión</h1>
        <p className="text-gray-600 mt-2">
          Accede a tu cuenta de forma segura
        </p>
      </div>
        <Formik
          initialValues={{ email: "", password: "" }}
          validationSchema={validationSchemas.login}
          onSubmit={handleSubmit}
          enableReinitialize
        >
          {({ isSubmitting, errors, touched }) => (
            <Form>
              {/* Global error message */}
              {(error || errors.general) && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <span className="text-red-700 text-sm">
                    {error || errors.general}
                  </span>
                </div>
              )}

              {/* Rate limiting warning */}
              {isBlocked && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center space-x-2">
                  <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
                  <div className="text-yellow-700 text-sm">
                    <p>Cuenta temporalmente bloqueada</p>
                    <p>Tiempo restante: {formatTime(remainingTime)}</p>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Correo Electrónico
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <Field
                      type="email"
                      name="email"
                      autoComplete="email"
                      className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                        touched.email && errors.email 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300'
                      }`}
                      placeholder="ejemplo@correo.com"
                      disabled={isBlocked || loading}
                    />
                  </div>
                  <ErrorMessage
                    name="email"
                    component="div"
                    className="mt-1 text-red-500 text-xs"
                  />
                </div>

                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <Field
                      type={showPassword ? "text" : "password"}
                      name="password"
                      autoComplete="current-password"
                      className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                        touched.password && errors.password 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300'
                      }`}
                      placeholder="Ingrese su contraseña"
                      disabled={isBlocked || loading}
                    />
                    <button
                      type="button"
                      onClick={togglePasswordVisibility}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 focus:outline-none"
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  <ErrorMessage
                    name="password"
                    component="div"
                    className="mt-1 text-red-500 text-xs"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting || isBlocked || loading}
                className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {(isSubmitting || loading) && (
                  <Loader2 className="w-5 h-5 animate-spin" />
                )}
                <span>
                  {isSubmitting || loading ? "Iniciando sesión..." : "Iniciar Sesión"}
                </span>
              </button>

              {/* Forgot Password Link */}
              <div className="text-center mt-4">
                <Link 
                  to="/forgot-password" 
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
                >
                  ¿Olvidaste tu contraseña?
                </Link>
              </div>
            </Form>
          )}
        </Formik>
    </div>
  );
};

export default LoginPage;
