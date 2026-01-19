import React, { createContext, useContext, useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'pstral_auth_token';
const USER_KEY = 'pstral_user';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Initialize from localStorage
    useEffect(() => {
        const savedToken = localStorage.getItem(TOKEN_KEY);
        const savedUser = localStorage.getItem(USER_KEY);
        
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
            // Verify token is still valid
            verifyToken(savedToken);
        } else {
            setLoading(false);
        }
    }, []);

    const verifyToken = async (tokenToVerify) => {
        try {
            const response = await fetch(`${API_URL}/auth/verify`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${tokenToVerify}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setUser(data.user);
                setToken(tokenToVerify);
            } else {
                // Token invalid, clear storage
                logout();
            }
        } catch (err) {
            console.error('Token verification failed:', err);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        setError(null);
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Échec de la connexion');
            }

            const data = await response.json();
            const accessToken = data.access_token;

            // Get user info
            const userResponse = await fetch(`${API_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!userResponse.ok) {
                throw new Error('Impossible de récupérer les informations utilisateur');
            }

            const userData = await userResponse.json();

            // Save to state and localStorage
            setToken(accessToken);
            setUser(userData);
            localStorage.setItem(TOKEN_KEY, accessToken);
            localStorage.setItem(USER_KEY, JSON.stringify(userData));

            return { success: true };
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        }
    };

    const register = async (userData) => {
        setError(null);
        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Échec de l\'inscription');
            }

            // Auto login after registration
            return await login(userData.username, userData.password);
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    };

    const value = {
        user,
        token,
        loading,
        error,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthProvider;

