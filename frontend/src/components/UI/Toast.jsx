import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

// Toast Context
const ToastContext = createContext();

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};

// Individual Toast Component
const ToastItem = ({ id, message, type, onRemove }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onRemove(id);
        }, 3000);
        return () => clearTimeout(timer);
    }, [id, onRemove]);

    const icons = {
        success: <CheckCircle size={18} className="text-emerald-400" />,
        error: <XCircle size={18} className="text-red-400" />,
        warning: <AlertCircle size={18} className="text-amber-400" />,
        info: <Info size={18} className="text-blue-400" />
    };

    const bgColors = {
        success: 'bg-emerald-500/10 border-emerald-500/30',
        error: 'bg-red-500/10 border-red-500/30',
        warning: 'bg-amber-500/10 border-amber-500/30',
        info: 'bg-blue-500/10 border-blue-500/30'
    };

    return (
        <div 
            className={`flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-xl shadow-2xl ${bgColors[type]} animate-in slide-in-from-right-5 duration-300`}
            role="alert"
        >
            {icons[type]}
            <span className="text-sm text-white font-medium">{message}</span>
            <button 
                onClick={() => onRemove(id)}
                className="ml-2 text-slate-400 hover:text-white transition-colors"
            >
                <X size={14} />
            </button>
        </div>
    );
};

// Toast Container
const ToastContainer = ({ toasts, removeToast }) => {
    if (toasts.length === 0) return null;
    
    return (
        <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2">
            {toasts.map(toast => (
                <ToastItem
                    key={toast.id}
                    {...toast}
                    onRemove={removeToast}
                />
            ))}
        </div>
    );
};

// Toast Provider
export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback((message, type = 'info') => {
        const id = Date.now() + Math.random();
        setToasts(prev => [...prev, { id, message, type }]);
    }, []);

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    const toast = {
        success: (message) => addToast(message, 'success'),
        error: (message) => addToast(message, 'error'),
        warning: (message) => addToast(message, 'warning'),
        info: (message) => addToast(message, 'info')
    };

    return (
        <ToastContext.Provider value={toast}>
            {children}
            <ToastContainer toasts={toasts} removeToast={removeToast} />
        </ToastContext.Provider>
    );
};

export default ToastProvider;

