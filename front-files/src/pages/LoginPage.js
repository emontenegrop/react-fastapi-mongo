// src/pages/LoginPage.js
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useAuth } from "../contexts/AuthContext";
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
import { Link } from "react-router-dom";

const LoginSchema = Yup.object().shape({
  email: Yup.string().email("Email inválido").required("El email es requerido"),
  password: Yup.string().required("La contraseña es requerida"),
});

const LoginPage = () => {
  const { login } = useAuth(); // Supongamos que este hook tiene la función login
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility

  const handleSubmit = async (values, { setSubmitting, setErrors }) => {
    //funciones de Formik para controlar el estado de envío y los errores.
    try {
      await login(values.email, values.password);
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setSubmitting(false);
    }
  }; // Función que se ejecuta al enviar el formulario

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  }; // Función utilizada  para mostrar el contenido del campo password

  return (
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
        <Formik
          initialValues={{ email: "", password: "" }} // Valores iniciales del formulario
          validationSchema={LoginSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting, errors }) => (
            <Form>
              <div className="mb-4">
                <label
                  htmlFor="email"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Email:
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <Field
                    type="email"
                    name="email"
                    className="shadow appearance-none border rounded w-full pl-10 pr-4 py-3 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Ingrese su email"
                  />
                  <ErrorMessage
                    name="email"
                    component="div"
                    className="text-red-500 text-xs italic"
                  />
                </div>
              </div>
              <div className="mb-6">
                <label
                  htmlFor="password"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Contraseña:
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <Field
                    // Dynamically set type based on showPassword state
                    type={showPassword ? "text" : "password"}
                    name="password"
                    className="shadow appearance-none border rounded w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Ingrese su contraseña"
                  />
                  <button
                    type="button" // Important: type="button" to prevent form submission
                    onClick={togglePasswordVisibility}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 focus:outline-none"
                    aria-label={
                      showPassword ? "Ocultar contraseña" : "Mostrar contraseña"
                    }
                  >
                    {/* Render Eye or EyeOff based on showPassword state */}
                    {showPassword ? (
                      <EyeOff className="w-5 h-5 text-gray-500" />
                    ) : (
                      <Eye className="w-5 h-5 text-gray-500" />
                    )}
                  </button>
                  <ErrorMessage
                    name="password"
                    component="div"
                    className="text-red-500 text-xs italic"
                  />
                </div>
              </div>
              {errors.general && (
                <div className="text-red-500 text-center mb-4">
                  {errors.general}
                </div>
              )}
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? "Iniciando sesión..." : "Iniciar Sesión"}
                </button>
              </div>
              <br></br>
              <div className="text-center mb-8">
              <Link to="/forgot-password" className="text-blue-600 hover:text-blue-800">
                  <p>¿Olvidaste tu contraseña?</p>
              </Link>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default LoginPage;
