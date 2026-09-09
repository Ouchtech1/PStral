import React from 'react';
import Markdown from 'react-markdown';
import { Clipboard, Copy } from 'lucide-react';
import { useToast } from '../UI/Toast';

const MessageBubble = ({ role, content, sources = [] }) => {
    const toast = useToast();
    const isUser = role === 'user';

    const copy = async (value, label) => {
        try {
            await navigator.clipboard.writeText(value);
            toast.success(`${label} copié dans le presse-papiers.`);
        } catch {
            toast.error('Copie indisponible ; sélectionnez le texte manuellement.');
        }
    };

    const markdownComponents = {
        // React renders children as text; no HTML string is injected.
        code({ inline, className, children, ...props }) {
            const value = String(children).replace(/\n$/, '');
            const isSql = /language-sql/i.test(className || '');
            if (inline) return <code className="bg-slate-800/80 rounded px-1.5 py-0.5 text-sm font-mono text-cyan-300" {...props}>{children}</code>;
            return (
                <div className="my-4 rounded-xl overflow-hidden border border-slate-700/50 bg-[#0d1117]">
                    <div className="flex items-center justify-between px-4 py-2 bg-slate-800/80 border-b border-slate-700/50">
                        <span className="text-xs text-slate-400 font-mono uppercase">{isSql ? 'sql oracle' : 'texte'}</span>
                        <button onClick={() => copy(value, isSql ? 'SQL' : 'Code')} className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-white/10" title="Copier">
                            <Clipboard size={12} /> Copier
                        </button>
                    </div>
                    <pre className="p-4 overflow-x-auto text-sm font-mono leading-relaxed text-slate-200"><code {...props}>{children}</code></pre>
                </div>
            );
        },
        a({ children }) {
            return <span className="text-slate-200 underline decoration-slate-600">{children}</span>;
        },
        img() {
            return null;
        },
    };

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[90%] md:max-w-[78%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
                <div className={`w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center border border-white/10 ${isUser ? 'bg-pack-gradient' : 'bg-cosmic-night'}`}>
                    <span className="text-white font-bold text-sm">{isUser ? 'U' : 'P'}</span>
                </div>
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} min-w-0`}>
                    <div className="text-xs font-semibold tracking-wide uppercase text-pack-blue mb-1">{isUser ? 'Vous' : 'Pstral'}</div>
                    <div className={`px-5 py-4 rounded-2xl shadow-xl border overflow-hidden ${isUser ? 'bg-gradient-to-br from-indigo-600 to-purple-700 text-white rounded-tr-sm border-indigo-500/30' : 'bg-glass-surface text-slate-200 rounded-tl-sm border-white/5'}`}>
                        {isUser ? <div className="whitespace-pre-wrap leading-relaxed">{content}</div> : (
                            <div className="prose prose-invert prose-p:leading-relaxed max-w-none">
                                <Markdown skipHtml components={markdownComponents}>{content}</Markdown>
                            </div>
                        )}
                    </div>
                    {!isUser && content && (
                        <div className="flex gap-1 mt-2 ml-1">
                            <button onClick={() => copy(content, 'Message')} className="p-1.5 text-slate-500 hover:text-white rounded-lg" title="Copier le message"><Copy size={14} /></button>
                        </div>
                    )}
                    {!isUser && sources.length > 0 && (
                        <details className="mt-2 ml-1 w-full text-xs text-slate-400">
                            <summary className="cursor-pointer hover:text-slate-200">Sources internes ({sources.length})</summary>
                            <div className="mt-2 space-y-2">
                                {sources.map((source, index) => (
                                    <div key={`${source.source_id || 'source'}-${index}`} className="rounded-lg border border-white/10 bg-white/5 p-2">
                                        <div className="text-slate-200">[S{index + 1}] {source.title}</div>
                                        <div>{source.section} · {source.version} · {source.date}</div>
                                        <div className="mt-1 text-slate-500">{source.excerpt}</div>
                                    </div>
                                ))}
                            </div>
                        </details>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
