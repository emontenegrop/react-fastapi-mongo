// src/pages/NotFoundPage.js
import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded shadow-md text-center">
                <h1 className="text-4xl font-bold text-gray-800 mb-4">404 - Página No Encontrada</h1>
                <p className="text-gray-700 mb-6">
                    Lo sentimos, la página que estás buscando no existe.
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

export default NotFoundPage;