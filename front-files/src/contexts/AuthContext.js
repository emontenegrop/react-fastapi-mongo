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
          const response = await axiosInstance.get("/api/auth/me");
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
      const response = await axiosInstance.post("/api/auth/login", {
        email,
        password,
      });
      const { token, user: userData } = response.data;
      localStorage.setItem("jwt_token", token); // Guarda el token JWT en localStorage
      axiosInstance.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${token}`;
      // Configura axios
      setUser(userData);      // Guarda los datos del usuario en el estado
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

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, loading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
