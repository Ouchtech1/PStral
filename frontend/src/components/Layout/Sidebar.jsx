import React from 'react';
import { LogOut, MessageSquare, Shield, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Logo from '../UI/PSTral.png';

const Sidebar = ({ onNewChat, mode }) => {
    const { user, logout } = useAuth();
    const modeLabel = mode === 'sql' ? 'SQL Oracle' : mode === 'chat' ? 'Questions métier' : 'Aucun dialogue actif';

    return (
        <aside className="flex flex-col h-full bg-cosmic-night/50 backdrop-blur-md border-r border-glass-border">
            <div className="p-6">
                <div className="flex items-center gap-3 mb-8">
                    <img src={Logo} alt="Pstral" className="h-10 w-auto" />
                    <p className="text-[10px] font-medium tracking-wider text-pack-blue uppercase">Pack Solutions</p>
                </div>
                <button
                    onClick={onNewChat}
                    className="w-full px-4 py-3.5 bg-pack-gradient rounded-xl text-sm font-semibold text-white"
                >
                    Nouvelle discussion
                </button>
            </div>
            <div className="px-6 text-sm text-slate-400 space-y-4">
                <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                    <div className="flex items-center gap-2 text-slate-200 font-medium">
                        <MessageSquare size={16} />
                        {modeLabel}
                    </div>
                    <p className="mt-2 text-xs leading-relaxed">
                        Les échanges sont supprimés au rechargement de la page et à la déconnexion.
                    </p>
                </div>
                <div className="p-4 rounded-2xl bg-pack-blue/10 border border-pack-blue/20 text-xs leading-relaxed">
                    Le SQL généré est à copier dans votre outil Oracle. Pstral n’exécute aucune requête.
                </div>
            </div>
            <div className="p-4 mt-auto">
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-pack-gradient flex items-center justify-center">
                            {user?.role === 'admin' ? <Shield size={16} /> : <User size={16} />}
                        </div>
                        <div className="min-w-0">
                            <div className="text-sm font-semibold text-white truncate">{user?.full_name || user?.username}</div>
                            <div className="text-xs text-slate-400">Session temporaire</div>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full mt-3 px-3 py-2 flex items-center justify-center gap-2 text-sm text-slate-400 hover:text-red-400"
                    >
                        <LogOut size={14} />
                        Déconnexion
                    </button>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
