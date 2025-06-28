// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from "react";
import axiosInstance from "../api/axios";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Estado para almacenar datos del usuario autenticado
  const [loading, setLoading] = useState(true); // Estado para controlar la carga inicial
  const navigate = useNavigate(); // Hook de react-router para redireccionar rutas

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("jwt_token"); // Obtiene el token JWT almacenado en localStorage
      if (token) {
        axiosInstance.defaults.headers.common[
          "Authorization"
        ] = `Bearer ${token}`; // Configura el header Authorization para todas las peticiones axios
        try {
          // Consulta al backend para obtener los datos del usuario autenticado
          const response = await axiosInstance.get("http://localhost:8082/api/v1/auth/me");
          setUser(response.data.user);
        } catch (error) {
          // Si falla la carga del usuario (token inválido o expirado), limpia el token y estado
          console.error("Error al cargar el usuario:", error);
          localStorage.removeItem("jwt_token");
          setUser(null);
        }
      }
      setLoading(false); // Indica que terminó la carga inicial
    };
    loadUser();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axiosInstance.post("http://localhost:8082/api/v1/auth/login", {
        email,
        password,
      });
      const { token, user: userData } = response.data;
      localStorage.setItem("jwt_token", token); // Guarda el token JWT en localStorage
      axiosInstance.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${token}`;
      // Configura axios
      setUser(userData); // Guarda los datos del usuario en el estado
      navigate("/dashboard"); // Redirige al dashboard tras login exitoso
      return true;
    } catch (error) {
      console.error(
        "Error en el login:",
        error.response?.data?.message || error.message
      );
      throw new Error(error.response?.data?.message || "Error de credenciales");
    }
  };

  const logout = () => {
    localStorage.removeItem("jwt_token"); // Elimina el token
    delete axiosInstance.defaults.headers.common["Authorization"];
    setUser(null); // Limpia el header Authorization
    navigate("/login"); // Redirige a la página de login
  };

  const sendPasswordResetEmail = async (email) => {
    try {
      // Validar que el email existe en la base de datos
      const response = await fetch("http://localhost:8082/api/v1/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Error al enviar el correo de recuperación"
        );
      }

      return data;
    } catch (error) {
      console.error("Error en sendPasswordResetEmail:", error);
      throw error;
    }
  };

  // // Ejemplo de endpoint del backend (Node.js/Express)
  // // /api/auth/forgot-password
  // const forgotPassword = async (req, res) => {
  //   try {
  //     const { email } = req.body;

  //     // Validar email
  //     if (!email) {
  //       return res.status(400).json({ message: "Email es requerido" });
  //     }

  //     // Verificar si el usuario existe
  //     const user = await User.findOne({ email });
  //     if (!user) {
  //       return res.status(404).json({ message: "Usuario no encontrado" });
  //     }

  //     // Generar token de recuperación
  //     const resetToken = crypto.randomBytes(32).toString("hex");
  //     const resetTokenExpiry = new Date(Date.now() + 5 * 60 * 1000); // 5 minutos

  //     // Guardar token en la base de datos
  //     user.resetPasswordToken = resetToken;
  //     user.resetPasswordExpiry = resetTokenExpiry;
  //     await user.save();

  //     // Crear enlace de recuperación
  //     const resetUrl = `${process.env.FRONTEND_URL}/reset-password/${resetToken}`;

  //     // Configurar el correo
  //     const mailOptions = {
  //       from: process.env.FROM_EMAIL,
  //       to: email,
  //       subject: "Recuperación de Contraseña - Tu App",
  //       html: `
  //       <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  //         <h2 style="color: #2563eb;">Recuperación de Contraseña</h2>
  //         <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>
  //         <div style="text-align: center; margin: 30px 0;">
  //           <a href="${resetUrl}" 
  //              style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block;">
  //             Restablecer Contraseña
  //           </a>
  //         </div>
  //         <div style="background-color: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0;">
  //           <p style="margin: 0; color: #92400e;">
  //             <strong>⚠️ Importante:</strong> Este enlace expirará en 5 minutos por razones de seguridad.
  //           </p>
  //         </div>
  //         <p style="color: #6b7280; font-size: 14px;">
  //           Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
  //         </p>
  //       </div>
  //     `,
  //     };

  //     // Enviar correo (usando nodemailer, sendgrid, etc.)
  //     await transporter.sendMail(mailOptions);

  //     res.status(200).json({
  //       message: "Correo de recuperación enviado exitosamente",
  //       email: email,
  //     });
  //   } catch (error) {
  //     console.error("Error en forgot password:", error);
  //     res.status(500).json({ message: "Error interno del servidor" });
  //   }
  // };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
        sendPasswordResetEmail,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
