// src/pages/SettingsPage.js
import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';
import { useAuth } from '../contexts/AuthContext'; // Importamos useAuth para mostrar información del usuario

const SettingsPage = () => {
    const { user } = useAuth(); // Obtenemos el usuario autenticado

    return (
        <DashboardLayout>
            <h1 className="text-3xl font-bold mb-6">Configuración de la Aplicación</h1>
            <div className="bg-white p-6 rounded shadow">
                <p className="text-lg mb-4">
                    Bienvenido a la página de configuración. Aquí puedes ajustar diversas opciones de la aplicación.
                </p>
                {user && user.role === 'admin' ? (
                    <div className="text-green-600 font-semibold">
                        <p>Tienes acceso completo a la configuración como administrador.</p>
                        <ul className="list-disc list-inside mt-2">
                            <li>Gestión de Usuarios</li>
                            <li>Configuración de Permisos</li>
                            <li>Ajustes del Sistema</li>
                        </ul>
                    </div>
                ) : (
                    <div className="text-orange-600 font-semibold">
                        <p>No tienes permisos de administrador para modificar estas configuraciones.</p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
};

export default SettingsPage;