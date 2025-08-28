// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { MenuProvider } from "./contexts/MenuContext";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ProtectedRoute from "./routes/ProtectedRoute";
import UnauthorizedPage from "./pages/UnauthorizedPage"; // Crea esta página
import NotFoundPage from "./pages/NotFoundPage"; // Crea esta página
import SettingsPage from "./pages/SettingsPage"; // Ejemplo de página
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";

function App() {
  return (
    <Router>
      <AuthProvider>
        <MenuProvider>
          {" "}
          {/* MenuProvider debe estar dentro de AuthProvider */}
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route
              path="/reset-password/:token"
              element={<ResetPasswordPage />}
            />

            {/* Rutas protegidas */}
            <Route
              element={<ProtectedRoute allowedRoles={["admin", "user"]} />}
            >
              <Route path="/dashboard" element={<DashboardPage />} />
              {/* Ruta solo para admin */}
              <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
            </Route>

            {/* Ruta por defecto o 404 */}
            <Route
              path="/"
              element={<ProtectedRoute allowedRoles={["admin", "user"]} />}
            >
              <Route index element={<DashboardPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </MenuProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
