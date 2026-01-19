import React from 'react'
import ReactDOM from 'react-dom/client'
import ErrorBoundary from './components/Layout/ErrorBoundary'
import { ToastProvider } from './components/UI/Toast'
import { AuthProvider } from './contexts/AuthContext'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ErrorBoundary>
            <AuthProvider>
                <ToastProvider>
                    <App />
                </ToastProvider>
            </AuthProvider>
        </ErrorBoundary>
    </React.StrictMode>,
)
