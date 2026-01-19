import React, { useState } from 'react';

const FeedbackModal = ({ isOpen, onClose, onSubmit, rating }) => {
    const [reason, setReason] = useState("");

    if (!isOpen) return null;

    const handleSubmit = () => {
        onSubmit(reason);
        setReason("");
    };


    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-cosmic-void/80 backdrop-blur-sm animate-in fade-in duration-200 p-4">
            <div className="glass-panel w-full max-w-lg rounded-2xl p-6 shadow-2xl animate-in zoom-in-95 duration-200 border border-white/10">
                <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${rating === 'like' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                        {rating === 'like' ? '👍' : '👎'}
                    </div>
                    <div>
                        <h3 className="text-xl font-semibold text-white">
                            {rating === 'like' ? "C'était utile ?" : "Que s'est-il passé ?"}
                        </h3>
                        <p className="text-sm text-slate-400">Votre avis compte pour nous.</p>
                    </div>
                </div>

                <div className="relative">
                    <textarea
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-nebula-purple/50 focus:border-nebula-purple/50 min-h-[120px] transition-all placeholder:text-slate-600 resize-none"
                        placeholder={rating === 'like' ? "Qu'est-ce qui a bien fonctionné..." : "Le code était incorrect ? La réponse était trop vague ?..."}
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                    />
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <button
                        onClick={onClose}
                        className="px-5 py-2.5 text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                    >
                        Ignorer
                    </button>
                    <button
                        onClick={handleSubmit}
                        className="px-6 py-2.5 text-sm font-semibold bg-white text-cosmic-night hover:bg-slate-200 rounded-xl shadow-lg shadow-white/10 hover:shadow-white/20 transition-all transform hover:-translate-y-0.5"
                    >
                        Envoyer
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FeedbackModal;
