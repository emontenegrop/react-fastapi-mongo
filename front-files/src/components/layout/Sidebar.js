// src/components/layout/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import { useMenu } from '../../contexts/MenuContext';

const Sidebar = () => {
    const { menuItems } = useMenu();

    return (
        <aside className="w-64 bg-gray-800 text-white p-4">
            <div className="text-2xl font-bold mb-6">Mi App</div>
            <nav>
                <ul>
                    {menuItems.map((item) => (
                        <li key={item.path} className="mb-2">
                            <NavLink
                                to={item.path}
                                className={({ isActive }) =>
                                    `block py-2 px-3 rounded hover:bg-gray-700 ${isActive ? 'bg-gray-700' : ''}`
                                }
                            >
                                {item.label}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;