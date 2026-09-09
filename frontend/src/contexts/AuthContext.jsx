import React, { createContext, useContext, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';
const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within an AuthProvider');
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [error, setError] = useState(null);
    const [sessionVersion, setSessionVersion] = useState(0);

    const login = async (username, password) => {
        setError(null);
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Échec de la connexion');

            const userResponse = await fetch(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${data.access_token}` },
            });
            const userData = await userResponse.json();
            if (!userResponse.ok) throw new Error(userData.detail || 'Impossible de récupérer le compte');

            setToken(data.access_token);
            setUser(userData);
            setSessionVersion((version) => version + 1);
            return { success: true };
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        setError(null);
        setSessionVersion((version) => version + 1);
    };

    return (
        <AuthContext.Provider value={{
            user, token, error, login, logout, sessionVersion,
            loading: false, isAuthenticated: Boolean(token && user),
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthProvider;
