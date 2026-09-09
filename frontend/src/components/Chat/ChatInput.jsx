import React, { useEffect, useRef, useState } from 'react';
import { SendHorizontal, Square } from 'lucide-react';

const ChatInput = ({ onSend, disabled, isGenerating, onStop, mode }) => {
    const [input, setInput] = useState('');
    const textareaRef = useRef(null);

    useEffect(() => {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = String(textareaRef.current.scrollHeight) + 'px';
    }, [input]);

    const submit = (event) => {
        event?.preventDefault();
        const content = input.trim();
        if (!content || disabled) return;
        onSend(content);
        setInput('');
    };

    return (
        <form onSubmit={submit} className="max-w-3xl w-full mx-auto p-4">
            <div className="relative w-full flex items-end gap-2 p-2 rounded-[2rem] shadow-2xl bg-cosmic-night/80 border border-glass-border">
                <textarea
                    ref={textareaRef}
                    rows={1}
                    maxLength={2000}
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    onKeyDown={(event) => {
                        if (event.key === 'Enter' && !event.shiftKey) submit(event);
                    }}
                    placeholder={mode === 'sql' ? 'Décrivez la requête Oracle souhaitée…' : 'Posez votre question métier…'}
                    disabled={disabled}
                    className="w-full bg-transparent border-none focus:ring-0 resize-none text-slate-200 placeholder-slate-500 py-4 px-4 max-h-[200px]"
                    style={{ minHeight: '52px' }}
                />
                {isGenerating ? (
                    <button type="button" onClick={onStop} className="p-3.5 rounded-full bg-red-500 text-white" title="Arrêter">
                        <Square size={18} fill="currentColor" />
                    </button>
                ) : (
                    <button
                        type="submit"
                        disabled={disabled || !input.trim()}
                        className="p-3.5 rounded-full bg-pack-gradient text-white disabled:opacity-50"
                        title="Envoyer"
                    >
                        <SendHorizontal size={20} />
                    </button>
                )}
            </div>
            <p className="mt-3 text-center text-[10px] text-slate-500 uppercase tracking-wide">
                Usage interne uniquement · aucune pièce jointe · 2 000 caractères maximum
            </p>
        </form>
    );
};

export default ChatInput;
