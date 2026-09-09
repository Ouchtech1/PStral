import React from 'react';

const ModeSelectionModal = ({ onSelectMode }) => {
    const modes = [
        {
            id: 'chat',
            label: 'Questions métier',
            icon: '💬',
            desc: 'Réponses fondées sur les documents internes indexés localement.',
        },
        {
            id: 'sql',
            label: 'SQL Oracle',
            icon: '⌘',
            desc: 'Requêtes à copier dans votre outil Oracle ; aucune exécution par Pstral.',
        },
    ];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-cosmic-void/90 backdrop-blur-sm p-4">
            <div className="glass-panel rounded-3xl p-8 max-w-3xl w-full shadow-2xl border border-white/10">
                <h1 className="text-3xl font-bold text-white text-center">Pstral</h1>
                <p className="text-slate-400 text-center mt-2 mb-8">Choisissez une fonction de démonstration.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {modes.map((mode) => (
                        <button
                            key={mode.id}
                            onClick={() => onSelectMode(mode.id)}
                            className="flex flex-col items-start p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-pack-blue/30 text-left"
                        >
                            <span className="text-3xl mb-4">{mode.icon}</span>
                            <span className="font-semibold text-lg text-white mb-2">{mode.label}</span>
                            <span className="text-sm text-slate-400 leading-relaxed">{mode.desc}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ModeSelectionModal;
