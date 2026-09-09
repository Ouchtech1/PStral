import React, { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { streamChat } from '../../services/api';
import ChatInput from './ChatInput';
import MessageBubble from './MessageBubble';
import Logo from '../UI/PSTral.png';

const assistantMessage = () => ({ role: 'assistant', content: '', sources: [], pending: true });

const ChatInterface = ({ mode }) => {
    const { token } = useAuth();
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('');
    const abortRef = useRef(null);
    const scrollRef = useRef(null);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, status]);

    useEffect(() => () => {
        // Abort the upstream fetch when the user logs out or starts a new
        // dialogue, so an old stream cannot keep consuming the demo slot.
        abortRef.current?.abort();
    }, []);

    const updateLastAssistant = (update) => {
        setMessages((previous) => {
            const updated = [...previous];
            const index = updated.length - 1;
            updated[index] = { ...updated[index], ...update };
            return updated;
        });
    };

    const streamResponse = async (history) => {
        abortRef.current = new AbortController();
        setMessages((previous) => [...previous, assistantMessage()]);
        setIsLoading(true);
        setError(null);
        setStatus('');
        let completed = false;

        try {
            for await (const event of streamChat(history, mode, token, abortRef.current.signal)) {
                if (!event || typeof event !== 'object') continue;
                if (event.type === 'status') {
                    setStatus(event.message || 'Traitement en cours…');
                } else if (event.type === 'sources') {
                    updateLastAssistant({ sources: event.sources || [] });
                } else if (event.type === 'token') {
                    setStatus('');
                    setMessages((previous) => {
                        const updated = [...previous];
                        const index = updated.length - 1;
                        updated[index] = {
                            ...updated[index],
                            content: `${updated[index].content || ''}${event.content || ''}`,
                            pending: false,
                        };
                        return updated;
                    });
                } else if (event.type === 'sql') {
                    setStatus('');
                    updateLastAssistant({ content: `\`\`\`sql\n${event.content}\n\`\`\``, pending: false, sql: true });
                } else if (['clarification', 'unsupported', 'error'].includes(event.type)) {
                    setStatus('');
                    updateLastAssistant({ content: event.message || 'La demande n’a pas pu être traitée.', pending: false });
                    if (event.type === 'error') setError(event.message);
                } else if (event.type === 'done') {
                    completed = true;
                    setStatus('');
                    updateLastAssistant({ pending: false, failed: event.success === false });
                }
            }
            if (!completed) {
                updateLastAssistant({ pending: false });
                setError('Le serveur a interrompu la réponse sans confirmation.');
            }
        } catch (err) {
            if (err.name === 'AbortError') {
                updateLastAssistant({ content: 'Génération arrêtée.', pending: false, stopped: true });
            } else {
                setMessages((previous) => previous[previous.length - 1]?.pending ? previous.slice(0, -1) : previous);
                setError(err.message || 'Erreur inattendue.');
            }
        } finally {
            setIsLoading(false);
            setStatus('');
            abortRef.current = null;
        }
    };

    const handleSend = async (content) => {
        if (isLoading || !token) return;
        const userMessage = { role: 'user', content };
        setMessages((previous) => [...previous, userMessage].slice(-20));
        // The API accepts only the role/content contract and at most two
        // previous exchanges. Do not forward UI-only fields such as sources
        // or pending, and keep the browser conversation display independent
        // from the bounded model context.
        const history = [...messages, userMessage]
            .filter((message) => message.content)
            .slice(-5)
            .map(({ role, content: messageContent }) => ({ role, content: messageContent }));
        await streamResponse(history);
    };

    const handleStop = () => abortRef.current?.abort();

    return (
        <div className="flex flex-col h-full w-full max-w-5xl mx-auto relative">
            {error && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 max-w-[90%] bg-red-500/10 border border-red-500/50 text-red-200 px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3">
                    <AlertTriangle size={18} />
                    <span className="text-sm">{error}</span>
                    <button onClick={() => setError(null)} className="ml-2 text-xs underline">Fermer</button>
                </div>
            )}
            <div className="flex-1 overflow-y-auto px-4 py-8 scrollbar-hide pt-20">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center animate-fade-in">
                        <img src={Logo} alt="Pstral" className="h-24 mb-6" />
                        <p className="text-sm text-slate-400 mb-4">{mode === 'sql' ? 'Génération de requêtes Oracle à copier' : 'Réponses fondées sur les documents internes indexés'}</p>
                        <div className="flex items-center gap-2 text-lg font-medium bg-pack-blue/10 px-4 py-1.5 rounded-full border border-pack-blue/20 text-pack-blue">Mode <span className="text-white font-bold">{mode === 'sql' ? 'SQL ORACLE' : 'QUESTIONS MÉTIER'}</span></div>
                    </div>
                ) : (
                    <div className="space-y-5">
                        {messages.map((message, index) => (
                            <React.Fragment key={`${index}-${message.role}`}>
                                {message.pending ? (
                                    <div className="flex items-center gap-3 text-sm text-emerald-300 px-12 py-2"><Loader2 size={16} className="animate-spin" />{status || 'Traitement en cours…'}</div>
                                ) : (
                                    <MessageBubble role={message.role} content={message.content} sources={message.sources} />
                                )}
                            </React.Fragment>
                        ))}
                    </div>
                )}
                <div ref={scrollRef} className="h-4" />
            </div>
            <div className="flex-shrink-0 pt-4 pb-5 px-4 z-30 pointer-events-none sticky bottom-0">
                <div className="pointer-events-auto max-w-4xl mx-auto"><ChatInput onSend={handleSend} disabled={isLoading || !token} isGenerating={isLoading} onStop={handleStop} mode={mode} /></div>
            </div>
        </div>
    );
};

export default ChatInterface;
