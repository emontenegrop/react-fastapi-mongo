// src/pages/DashboardPage.js
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axiosInstance from '../api/axios';
import DashboardLayout from '../components/layout/DashboardLayout';

const DashboardPage = () => {
    const { user } = useAuth();
    const [profileData, setProfileData] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await axiosInstance.get('http://localhost:8082/api/v1/auth/me');
                setProfileData(response.data.user);
            } catch (error) {
                console.error("Error al obtener el perfil:", error);
            }
        };
        if (user) {
            fetchProfile();
        }
    }, [user]);

    return (
        <DashboardLayout>
            <h1 className="text-3xl font-bold mb-6">Bienvenido al Dashboard, {user?.name}!</h1>
            {profileData && (
                <div className="bg-white p-6 rounded shadow">
                    <h2 className="text-xl font-semibold mb-4">Tu Perfil</h2>
                    <p><strong>Email:</strong> {profileData.email}</p>
                    <p><strong>Rol:</strong> {profileData.role}</p>
                </div>
            )}
        </DashboardLayout>
    );
};

export default DashboardPage;