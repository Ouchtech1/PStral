import React, { useRef } from 'react';
import { Trash2, Upload, MessageSquare, LogOut, Shield, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Logo from '../UI/PSTral.png';

const Sidebar = ({ onNewChat, sessions = [], currentSessionId, onSelectSession, onDeleteSession, onImportChat }) => {
    const fileInputRef = useRef(null);
    const { user, logout } = useAuth();

    return (
        <div className="flex flex-col h-full bg-cosmic-night/50 backdrop-blur-md border-r border-glass-border">
            <div className="p-6">
                <div className="flex items-center gap-3 mb-8">
                    <img src={Logo} alt="PSTral" className="h-10 w-auto" />
                    <p className="text-[10px] font-medium tracking-wider text-pack-blue uppercase">Pack Solutions</p>
                </div>

                <button
                    onClick={onNewChat}
                    className="group relative w-full px-4 py-3.5 bg-pack-gradient rounded-xl text-sm font-semibold text-white shadow-lg shadow-pack-blue/20 hover:shadow-pack-blue/40 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
                >
                    <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                    <div className="relative flex items-center justify-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                        <span>Nouvelle discussion</span>
                    </div>
                </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4 space-y-2 scrollbar-thin">
                <div className="px-2 py-2 text-[10px] font-bold tracking-widest text-slate-500 uppercase flex justify-between items-center">
                    <span>Historique</span>
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-1.5 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                        title="Importer"
                    >
                        <Upload size={12} />
                    </button>
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".json"
                        onChange={onImportChat}
                    />
                </div>

                {sessions.length === 0 && (
                    <div className="text-center py-8">
                        <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl opacity-50">Draft</div>
                        <p className="text-xs text-slate-500">Aucune discussion récente</p>
                    </div>
                )}

                <div className="space-y-1">
                    {sessions.map(session => (
                        <div
                            key={session.id}
                            onClick={() => onSelectSession(session.id)}
                            className={`group relative w-full flex items-center justify-between px-3 py-3 rounded-xl cursor-pointer transition-all duration-200 border border-transparent ${session.id === currentSessionId
                                ? 'bg-gradient-to-r from-white/10 to-transparent border-white/5 text-white shadow-sm'
                                : 'hover:bg-white/5 text-slate-400 hover:text-slate-200'
                                }`}
                        >
                            <div className="flex items-center gap-3 overflow-hidden">
                                <MessageSquare size={16} className={`flex-shrink-0 ${session.id === currentSessionId ? 'text-nebula-blue' : 'opacity-70'}`} />
                                <div className="text-sm font-medium truncate">
                                    {session.title || 'Discussion sans titre'}
                                </div>
                            </div>
                            <button
                                onClick={(e) => onDeleteSession(e, session.id)}
                                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded-lg transition-all"
                                title="Supprimer"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-4 mt-auto">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/5 backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-pack-gradient p-[2px] flex-shrink-0">
                            <div className="w-full h-full rounded-full bg-cosmic-night flex items-center justify-center">
                                {user?.role === 'admin' ? (
                                    <Shield size={16} className="text-pack-blue" />
                                ) : (
                                    <User size={16} className="text-pack-blue" />
                                )}
                            </div>
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-white truncate">
                                {user?.full_name || user?.username || 'Utilisateur'}
                            </div>
                            <div className="text-xs text-slate-400 truncate">
                                {user?.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full mt-3 px-3 py-2 flex items-center justify-center gap-2 text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors border border-transparent hover:border-red-500/20"
                    >
                        <LogOut size={14} />
                        <span>Déconnexion</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
