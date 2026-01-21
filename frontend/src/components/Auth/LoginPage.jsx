import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Eye, EyeOff, LogIn, UserPlus, Loader2, Shield } from 'lucide-react';
import Logo from '../UI/PSTral.png';

const LoginPage = () => {
    const { login, register, error: authError } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        full_name: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (!isLogin) {
            if (formData.password !== formData.confirmPassword) {
                setError('Les mots de passe ne correspondent pas');
                setLoading(false);
                return;
            }
            if (formData.password.length < 6) {
                setError('Le mot de passe doit contenir au moins 6 caractères');
                setLoading(false);
                return;
            }
        }

        try {
            let result;
            if (isLogin) {
                result = await login(formData.username, formData.password);
            } else {
                result = await register({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    full_name: formData.full_name
                });
            }

            if (!result.success) {
                setError(result.error);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError(null);
        setFormData({
            username: '',
            email: '',
            password: '',
            full_name: '',
            confirmPassword: ''
        });
    };

    return (
        <div className="min-h-screen bg-pack-bg-light bg-pack-bg-gradient flex items-center justify-center p-4 relative overflow-hidden">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-pack-blue/10 rounded-full blur-3xl animate-pulse-slow"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse-slow [animation-delay:2s]"></div>
            </div>

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <img src={Logo} alt="PSTral" className="h-20 mx-auto mb-4 animate-float" />
                    <p className="text-slate-400 mt-2">Assistant IA Pack Solutions</p>
                </div>

                <div className="glass-panel rounded-3xl p-8 shadow-2xl border border-white/10 backdrop-blur-xl">
                    <div className="flex items-center justify-center gap-2 mb-6">
                        <Shield size={20} className="text-pack-blue" />
                        <h2 className="text-xl font-semibold text-white">
                            {isLogin ? 'Connexion' : 'Créer un compte'}
                        </h2>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                {isLogin ? 'Identifiant ou email' : 'Nom d\'utilisateur'}
                            </label>
                            <input
                                type="text"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 focus:border-pack-blue/50 transition-all"
                                placeholder="votre.identifiant"
                                required
                                autoComplete="username"
                            />
                        </div>

                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                    Adresse email
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 focus:border-pack-blue/50 transition-all"
                                    placeholder="vous@pack-solutions.com"
                                    required
                                    autoComplete="email"
                                />
                            </div>
                        )}

                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                    Nom complet
                                </label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 focus:border-pack-blue/50 transition-all"
                                    placeholder="Prénom Nom"
                                    required
                                    autoComplete="name"
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                Mot de passe
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 focus:border-pack-blue/50 transition-all pr-12"
                                    placeholder="••••••••"
                                    required
                                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                    Confirmer le mot de passe
                                </label>
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 focus:border-pack-blue/50 transition-all"
                                    placeholder="••••••••"
                                    required
                                    autoComplete="new-password"
                                />
                            </div>
                        )}

                        {(error || authError) && (
                            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-sm">
                                {error || authError}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3.5 bg-pack-gradient text-white font-semibold rounded-xl shadow-lg shadow-pack-blue/25 hover:shadow-pack-blue/40 hover:-translate-y-0.5 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <Loader2 size={20} className="animate-spin" />
                            ) : isLogin ? (
                                <>
                                    <LogIn size={18} />
                                    Se connecter
                                </>
                            ) : (
                                <>
                                    <UserPlus size={18} />
                                    Créer le compte
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-slate-400 text-sm">
                            {isLogin ? "Pas encore de compte ?" : "Déjà inscrit ?"}
                            <button
                                type="button"
                                onClick={toggleMode}
                                className="ml-2 text-pack-blue hover:text-white font-medium transition-colors"
                            >
                                {isLogin ? "S'inscrire" : "Se connecter"}
                            </button>
                        </p>
                    </div>
                </div>

                <div className="mt-6 text-center">
                    <p className="text-xs text-slate-500">
                        Usage interne uniquement • Pack Solutions © {new Date().getFullYear()}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;

