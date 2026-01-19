import React from 'react';

const ModeSelectionModal = ({ onSelectMode }) => {
    const modes = [
        { id: 'sql', label: 'Générateur SQL', icon: '💾', desc: 'Convertir le langage naturel en requêtes Oracle SQL.' },
        { id: 'email', label: 'Assistant Email', icon: '📧', desc: 'Rédiger des emails professionnels.' },
        { id: 'wiki', label: 'Rédacteur Wiki', icon: '📝', desc: 'Créer de la documentation technique.' },
        { id: 'chat', label: 'Discussion Générale', icon: '💬', desc: 'Discutez naturellement avec l\'assistant.' },
    ];


    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-cosmic-void/90 backdrop-blur-sm p-4 animate-in fade-in duration-300">
            <div className="glass-panel rounded-3xl p-8 max-w-3xl w-full shadow-2xl animate-in zoom-in-95 duration-300 border border-white/10 relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-pack-gradient opacity-50"></div>

                {/* Logo */}
                <div className="flex justify-center mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-pack-gradient flex items-center justify-center shadow-lg shadow-pack-blue/20">
                        <span className="text-3xl font-bold text-white">P</span>
                    </div>
                </div>

                <h2 className="text-3xl font-bold text-white mb-2 text-center tracking-tight">
                    Bienvenue sur Pstral
                </h2>
                <p className="text-pack-blue text-center text-sm mb-2 font-medium">Assistant IA Pack Solutions</p>
                <p className="text-slate-400 text-center mb-8 font-light">Sélectionnez un mode spécialisé pour commencer votre session.</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {modes.map((mode) => (
                        <button
                            key={mode.id}
                            onClick={() => onSelectMode(mode.id)}
                            className="group relative flex flex-col items-start p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-pack-blue/30 transition-all duration-300 text-left overflow-hidden hover:shadow-lg hover:shadow-pack-blue/10"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-10 translate-x-4 -translate-y-4 group-hover:translate-x-0 group-hover:translate-y-0 transition-all duration-500 text-6xl select-none grayscale">
                                {mode.icon}
                            </div>

                            <div className="w-12 h-12 rounded-xl bg-pack-blue/10 border border-pack-blue/20 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-300 shadow-inner">
                                {mode.icon}
                            </div>

                            <div className="font-semibold text-lg text-white mb-2 group-hover:text-pack-blue transition-colors">
                                {mode.label}
                            </div>
                            <div className="text-sm text-slate-400 font-light leading-relaxed group-hover:text-slate-300">
                                {mode.desc}
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ModeSelectionModal;
