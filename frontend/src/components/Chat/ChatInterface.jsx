import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { streamChat, sendFeedback } from '../../services/api';
import { Download, FileText } from 'lucide-react';
import FeedbackModal from '../UI/FeedbackModal';
import { useToast } from '../UI/Toast';
import Logo from '../UI/PSTral.png';


const ChatInterface = ({ mode, sessionId, onUpdateTitle }) => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
    const [currentFeedback, setCurrentFeedback] = useState(null);
    const [titleGenerated, setTitleGenerated] = useState(false);
    const scrollRef = useRef(null);
    const abortRef = useRef(null);
    const toast = useToast();

    const generateTitle = (content) => {
        if (!content) return "Nouvelle discussion";
        const words = content.trim().split(/\s+/).slice(0, 6).join(' ');
        return words.length > 40 ? words.substring(0, 37) + '...' : words;
    };

    useEffect(() => {
        if (!sessionId) return;
            const saved = localStorage.getItem(`ministral_chat_${sessionId}`);
            if (saved) {
                try {
                const loaded = JSON.parse(saved);
                setMessages(loaded);
                if (loaded.length > 0) setTitleGenerated(true);
                } catch (e) {
                console.error("Erreur chargement:", e);
            }
        }
    }, [sessionId]);

    useEffect(() => {
        if (sessionId && messages.length > 0) {
            localStorage.setItem(`ministral_chat_${sessionId}`, JSON.stringify(messages));
        }
    }, [messages, sessionId]);

    const scrollToBottom = () => scrollRef.current?.scrollIntoView({ behavior: "smooth" });

    useEffect(() => { if (error) setError(null); }, [messages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const streamResponse = async (history) => {
        abortRef.current = new AbortController();
            setMessages(prev => [...prev, { role: 'assistant', content: '', isThinking: true }]);

        try {
            const generator = streamChat(history, mode, abortRef.current.signal);
            let fullContent = "";

            for await (const chunk of generator) {
                fullContent += chunk;
                setMessages(prev => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { role: 'assistant', content: fullContent, isThinking: false };
                    return updated;
                });
            }
        } catch (err) {
            if (err.name === 'AbortError') {
            setMessages(prev => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    if (last.role === 'assistant') {
                        updated[updated.length - 1] = { ...last, isThinking: false, content: last.content + " [Arrêté]" };
                    }
                    return updated;
                });
            } else {
                setMessages(prev => prev[prev.length - 1]?.isThinking ? prev.slice(0, -1) : prev);
                setError(err.message || "Erreur inattendue");
            }
        } finally {
            setIsLoading(false);
            abortRef.current = null;
        }
    };

    const handleSendMessage = async (payload) => {
        const content = typeof payload === 'object' ? payload.content : payload;
        const images = typeof payload === 'object' ? (payload.images || []) : [];
        const userMessage = { role: 'user', content, images };
        
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        if (!titleGenerated && messages.length === 0 && onUpdateTitle) {
            onUpdateTitle(generateTitle(content));
            setTitleGenerated(true);
        }

        await streamResponse([...messages, userMessage]);
    };

    const handleStopGeneration = () => abortRef.current?.abort();

    const handleRegenerate = async () => {
        if (isLoading || messages.length < 2) return;
        const lastIdx = messages.length - 1;
        if (messages[lastIdx]?.role !== 'assistant' || messages[lastIdx - 1]?.role !== 'user') return;

        const history = messages.slice(0, -1);
        setMessages(history);
        setIsLoading(true);
        setError(null);

        await streamResponse(history);
    };

    const handleExportJSON = () => {
        const data = {
            mode,
            title: `Conversation Pstral - ${mode}`,
            exportedAt: new Date().toISOString(),
            messages
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pstral-chat-${sessionId}-${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success('Conversation exportée en JSON');
    };

    const handleExportPDF = () => {
        // Create a printable HTML document and use browser print to PDF
        const printWindow = window.open('', '_blank');
        const date = new Date().toLocaleDateString('fr-FR');
        
        const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pstral - Conversation ${mode} - ${date}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            padding: 40px; 
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            padding-bottom: 20px; 
            border-bottom: 2px solid #0066CC; 
        }
        .header h1 { 
            color: #0066CC; 
            font-size: 28px; 
            margin-bottom: 8px;
        }
        .header .meta { 
            color: #64748b; 
            font-size: 14px; 
        }
        .message { 
            margin-bottom: 24px; 
            padding: 16px 20px; 
            border-radius: 12px; 
        }
        .message.user { 
            background: linear-gradient(135deg, #0066CC 0%, #663399 100%); 
            color: white; 
            margin-left: 60px; 
        }
        .message.assistant { 
            background: white; 
            border: 1px solid #e2e8f0; 
            margin-right: 60px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .message .role { 
            font-weight: 600; 
            font-size: 12px; 
            text-transform: uppercase; 
            letter-spacing: 0.5px;
            margin-bottom: 8px; 
        }
        .message.user .role { color: rgba(255,255,255,0.8); }
        .message.assistant .role { color: #0066CC; }
        .message .content { white-space: pre-wrap; }
        pre { 
            background: #1e293b; 
            color: #e2e8f0; 
            padding: 16px; 
            border-radius: 8px; 
            overflow-x: auto; 
            margin: 12px 0;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 13px;
        }
        code { 
            background: #f1f5f9; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 13px;
        }
        .footer { 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #e2e8f0; 
            text-align: center; 
            color: #94a3b8; 
            font-size: 12px; 
        }
        @media print {
            body { padding: 20px; }
            .message { break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✨ Pstral</h1>
        <div class="meta">Mode: ${mode?.toUpperCase()} | Exporté le ${date}</div>
    </div>
    ${messages.map(msg => `
        <div class="message ${msg.role}">
            <div class="role">${msg.role === 'user' ? 'Vous' : 'Pstral'}</div>
            <div class="content">${escapeHtml(msg.content)}</div>
        </div>
    `).join('')}
    <div class="footer">
        Document généré par Pstral - Assistant IA Pack Solutions<br/>
        Usage interne uniquement
    </div>
</body>
</html>`;
        
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        printWindow.focus();
        
        // Auto-trigger print dialog
        setTimeout(() => {
            printWindow.print();
        }, 500);
        
        toast.info('Utilisez "Enregistrer en PDF" dans la boîte de dialogue d\'impression');
    };

    // Helper to escape HTML
    const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    const handleOpenFeedback = (index, rating) => {
        setCurrentFeedback({ messageIndex: index, rating });
        setFeedbackModalOpen(true);
    };

    const handleSubmitFeedback = async (reason) => {
        if (!currentFeedback) return;

        const { messageIndex, rating } = currentFeedback;
        const agentMessage = messages[messageIndex];
        // Ideally we find the user message before this one
        const userMessage = messages[messageIndex - 1];

        if (agentMessage && userMessage) {
            try {
                await sendFeedback({
                    user_question: userMessage.content,
                    agent_answer: agentMessage.content,
                    rating,
                    reason
                });
                toast.success('Merci pour votre feedback ! 🎉');
            } catch (e) {
                console.error("Failed to send feedback", e);
                toast.error('Échec de l\'envoi du feedback');
            }
        }
        setFeedbackModalOpen(false);
        setCurrentFeedback(null);
    };

    return (
        <div className="flex flex-col h-full w-full max-w-5xl mx-auto relative">

            <div className="absolute top-4 right-4 z-40 flex gap-2">
                {messages.length > 0 && (
                    <>
                    <button
                            onClick={handleExportJSON}
                            className="glass-button p-2 text-slate-300 rounded-lg flex items-center gap-2 text-xs border border-glass-border hover:bg-white/10 transition-colors"
                            title="Exporter en JSON"
                    >
                        <Download size={14} />
                            JSON
                        </button>
                        <button
                            onClick={handleExportPDF}
                            className="glass-button p-2 text-slate-300 rounded-lg flex items-center gap-2 text-xs border border-glass-border hover:bg-white/10 transition-colors"
                            title="Exporter en PDF"
                        >
                            <FileText size={14} />
                            PDF
                    </button>
                    </>
                )}
            </div>

            {error && (
                <div className="absolute top-20 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-top-2">
                    <div className="bg-red-500/10 border border-red-500/50 text-red-200 px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">⚠️</span>
                            <span>{error}</span>
                        </div>
                        <button onClick={() => setError(null)} className="hover:bg-red-500/20 p-1 rounded-full">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                    </div>
                </div>
            )}

            <div className="flex-1 overflow-y-auto px-4 py-8 scrollbar-hide pt-20">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center animate-fade-in">
                        <img src={Logo} alt="PSTral" className="h-24 mb-6 animate-float" />
                        <p className="text-sm text-slate-400 mb-4">Assistant IA Pack Solutions</p>
                        <div className="flex items-center gap-2 text-lg font-medium bg-pack-blue/10 px-4 py-1.5 rounded-full border border-pack-blue/20 text-pack-blue">
                            Mode <span className="text-white font-bold">{mode?.toUpperCase()}</span>
                        </div>
                    </div>

                ) : (
                    <div className="space-y-6">
                        {messages.map((msg, idx) => {
                            const isLast = msg.role === 'assistant' && idx === messages.length - 1 && !msg.isThinking;
                            return (
                            <MessageBubble
                                key={idx}
                                role={msg.role}
                                content={msg.content}
                                isThinking={msg.isThinking}
                                images={msg.images}
                                onFeedback={(rating) => handleOpenFeedback(idx, rating)}
                                    onRegenerate={handleRegenerate}
                                    isLastAssistantMessage={isLast}
                            />
                            );
                        })}
                    </div>
                )}
                <div ref={scrollRef} className="h-4" />
            </div>

            <div className="flex-shrink-0 pt-6 pb-6 px-4 z-30 pointer-events-none sticky bottom-0">
                <div className="pointer-events-auto max-w-4xl mx-auto">
                    <ChatInput 
                        onSend={handleSendMessage} 
                        disabled={isLoading}
                        isGenerating={isLoading}
                        onStop={handleStopGeneration}
                    />
                </div>
            </div>

            <FeedbackModal
                isOpen={feedbackModalOpen}
                onClose={() => setFeedbackModalOpen(false)}
                onSubmit={handleSubmitFeedback}
                rating={currentFeedback?.rating}
            />
        </div>

    );
};

export default ChatInterface;
