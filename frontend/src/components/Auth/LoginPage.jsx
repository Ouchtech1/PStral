import React, { useState } from 'react';
import { Eye, EyeOff, LogIn, Loader2, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Logo from '../UI/PSTral.png';

const LoginPage = () => {
    const { login, error: authError } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        await login(username, password);
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-pack-bg-light bg-pack-bg-gradient flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <img src={Logo} alt="Pstral" className="h-20 mx-auto mb-4" />
                    <p className="text-slate-400">Assistant IA interne Pack Solutions</p>
                </div>
                <div className="glass-panel rounded-3xl p-8 shadow-2xl border border-white/10">
                    <div className="flex items-center justify-center gap-2 mb-6">
                        <Shield size={20} className="text-pack-blue" />
                        <h1 className="text-xl font-semibold text-white">Connexion</h1>
                    </div>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <label className="block text-sm font-medium text-slate-300">
                            Identifiant ou email
                            <input
                                className="mt-1.5 w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                                value={username}
                                onChange={(event) => setUsername(event.target.value)}
                                autoComplete="username"
                                required
                            />
                        </label>
                        <label className="block text-sm font-medium text-slate-300">
                            Mot de passe
                            <span className="relative block mt-1.5">
                                <input
                                    className="w-full px-4 py-3 pr-12 bg-white/5 border border-white/10 rounded-xl text-white"
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(event) => setPassword(event.target.value)}
                                    autoComplete="current-password"
                                    required
                                />
                                <button
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
                                    type="button"
                                    onClick={() => setShowPassword((visible) => !visible)}
                                    aria-label="Afficher ou masquer le mot de passe"
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </span>
                        </label>
                        {authError && <p role="alert" className="text-sm text-red-300">{authError}</p>}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3.5 bg-pack-gradient text-white font-semibold rounded-xl flex justify-center gap-2 disabled:opacity-50"
                        >
                            {loading ? <Loader2 size={20} className="animate-spin" /> : <LogIn size={18} />}
                            Se connecter
                        </button>
                    </form>
                </div>
                <p className="mt-6 text-center text-xs text-slate-500">
                    Les comptes sont créés par l’administrateur de la démonstration.
                </p>
            </div>
        </div>
    );
};

export default LoginPage;
