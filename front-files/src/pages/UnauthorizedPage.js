// src/pages/UnauthorizedPage.js
import React from 'react';
import { Link } from 'react-router-dom';

const UnauthorizedPage = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded shadow-md text-center">
                <h1 className="text-4xl font-bold text-red-600 mb-4">403 - Acceso Denegado</h1>
                <p className="text-gray-700 mb-6">
                    No tienes permiso para acceder a esta página.
                </p>
                <Link
                    to="/dashboard"
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                    Volver al Dashboard
                </Link>
            </div>
        </div>
    );
};

export default UnauthorizedPage;