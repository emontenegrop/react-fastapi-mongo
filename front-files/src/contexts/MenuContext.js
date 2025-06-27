// src/contexts/MenuContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import axiosInstance from '../api/axios';
import { useAuth } from './AuthContext';

const MenuContext = createContext(null);

export const MenuProvider = ({ children }) => {
    const [menuItems, setMenuItems] = useState([]);
    const { isAuthenticated, user } = useAuth();

    useEffect(() => {
        const fetchMenu = async () => {
            if (isAuthenticated && user?.role) {
                try {
                    // El backend debe devolver las opciones de menú basadas en el rol
                    const response = await axiosInstance.get(`/api/menu?role=${user.role}`);
                    setMenuItems(response.data.menu);
                } catch (error) {
                    console.error("Error al obtener el menú:", error);
                    setMenuItems([]); // Limpiar menú en caso de error
                }
            } else {
                setMenuItems([]);
            }
        };
        fetchMenu();
    }, [isAuthenticated, user]);

    return (
        <MenuContext.Provider value={{ menuItems }}>
            {children}
        </MenuContext.Provider>
    );
};

export const useMenu = () => useContext(MenuContext);