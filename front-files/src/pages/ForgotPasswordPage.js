// src/pages/ForgotPasswordPage.js
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useAuth } from "../contexts/AuthContext";
import {
  Mail,
  Shield,
  ArrowLeft,
  CheckCircle,
  Clock,
  Send,
} from "lucide-react";
import { Link } from "react-router-dom"; // Asumiendo que usas React Router

const ForgotPasswordSchema = Yup.object().shape({
  email: Yup.string().email("Email inválido").required("El email es requerido"),
});

const ForgotPasswordPage = () => {
  const { sendPasswordResetEmail } = useAuth(); // Función para enviar email de recuperación
  const [emailSent, setEmailSent] = useState(false);
  const [sentEmail, setSentEmail] = useState("");

  const handleSubmit = async (values, { setSubmitting, setErrors }) => {
    try {
      // Enviar solicitud de recuperación de contraseña
      await sendPasswordResetEmail(values.email);
      setSentEmail(values.email);
      setEmailSent(true);
    } catch (error) {
      setErrors({
        general: error.message || "Error al enviar el correo de recuperación",
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Vista después de enviar el email
  if (emailSent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              ¡Correo Enviado!
            </h1>
            <p className="text-gray-600 mt-2">Revisa tu bandeja de entrada</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <Mail className="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p className="text-green-800 font-medium">Correo enviado a:</p>
                <p className="text-green-700 text-sm break-all">{sentEmail}</p>
              </div>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <Clock className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p className="text-amber-800 font-medium">
                  Tiempo límite: 5 minutos
                </p>
                <p className="text-amber-700 text-sm">
                  El enlace de recuperación expirará en 5 minutos por seguridad.
                </p>
              </div>
            </div>
          </div>

          <div className="text-center text-sm text-gray-600 mb-6">
            <p>
              Si no ves el correo, revisa tu carpeta de spam o correo no
              deseado.
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => setEmailSent(false)}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all"
            >
              Enviar otro correo
            </button>

            <Link
              to="/login"
              className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all flex items-center justify-center"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver al login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Vista principal del formulario
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Recuperar Contraseña
          </h1>
          <p className="text-gray-600 mt-2">
            Ingresa tu email para recibir un enlace de recuperación
          </p>
        </div>

        <Formik
          initialValues={{ email: "" }}
          validationSchema={ForgotPasswordSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting, errors }) => (
            <Form>
              <div className="mb-6">
                <label
                  htmlFor="email"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Correo Electrónico:
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <Field
                    type="email"
                    name="email"
                    className="shadow appearance-none border rounded w-full pl-10 pr-4 py-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="ejemplo@correo.com"
                  />
                  <ErrorMessage
                    name="email"
                    component="div"
                    className="text-red-500 text-xs italic mt-1"
                  />
                </div>
              </div>

              {errors.general && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                  {errors.general}
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-start">
                  <Clock className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <p className="text-blue-800 font-medium text-sm">
                      Información importante:
                    </p>
                    <p className="text-blue-700 text-sm mt-1">
                      El enlace de recuperación será válido por solo 5 minutos
                      por razones de seguridad.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Enviar Enlace de Recuperación
                    </>
                  )}
                </button>

                <Link
                  to="/login"
                  className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all flex items-center justify-center"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver al login
                </Link>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
