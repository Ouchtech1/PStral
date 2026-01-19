import React, { useState } from 'react';
import Markdown from 'react-markdown';
import { Clipboard, ThumbsUp, ThumbsDown, RefreshCw, Copy, Play, Loader2 } from 'lucide-react';
import { useToast } from '../UI/Toast';
import { executeSQL } from '../../services/api';
import SQLResultsModal from './SQLResultsModal';


const MessageBubble = ({ role, content, isThinking, images, onFeedback, onRegenerate, isLastAssistantMessage = false }) => {
    const toast = useToast();
    const isUser = role === 'user';
    
    const [sqlModalOpen, setSqlModalOpen] = useState(false);
    const [sqlResults, setSqlResults] = useState(null);
    const [executingSQL, setExecutingSQL] = useState(false);
    const [currentQuery, setCurrentQuery] = useState('');

    const handleCopyCode = async (code) => {
        try {
            await navigator.clipboard.writeText(code);
            toast.success('Code copié dans le presse-papiers !');
        } catch (err) {
            toast.error('Échec de la copie');
        }
    };

    const handleCopyMessage = async () => {
        try {
            await navigator.clipboard.writeText(content);
            toast.success('Message copié !');
        } catch (err) {
            toast.error('Échec de la copie');
        }
    };

    const handleExecuteSQL = async (query) => {
        setExecutingSQL(true);
        setCurrentQuery(query);
        try {
            const results = await executeSQL(query);
            setSqlResults(results);
            setSqlModalOpen(true);
            if (results.success) {
                toast.success(`Requête exécutée: ${results.row_count} ligne(s)`);
            }
        } catch (err) {
            setSqlResults({
                success: false,
                columns: [],
                rows: [],
                row_count: 0,
                error: err.message
            });
            setSqlModalOpen(true);
            toast.error('Erreur lors de l\'exécution SQL');
        } finally {
            setExecutingSQL(false);
        }
    };

    const components = {
        p({ children }) {
            return <div className="prose-p mb-4">{children}</div>;
        },
        code({ node, inline, className, children, ...codeProps }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : 'code';
            const codeContent = String(children).replace(/\n$/, '');
            
            const highlightSQL = (code) => {
                const keywords = /\b(SELECT|FROM|WHERE|AND|OR|NOT|IN|LIKE|BETWEEN|IS|NULL|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|CROSS|ON|GROUP|BY|ORDER|ASC|DESC|HAVING|LIMIT|OFFSET|UNION|INTERSECT|EXCEPT|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|INDEX|VIEW|DROP|ALTER|ADD|COLUMN|PRIMARY|KEY|FOREIGN|REFERENCES|CONSTRAINT|UNIQUE|DEFAULT|CHECK|CASCADE|AS|DISTINCT|ALL|EXISTS|ANY|SOME|CASE|WHEN|THEN|ELSE|END|COUNT|SUM|AVG|MIN|MAX|COALESCE|NULLIF|CAST|CONVERT)\b/gi;
                const strings = /('[^']*'|"[^"]*")/g;
                const numbers = /\b(\d+\.?\d*)\b/g;
                const comments = /(--.*$|\/\*[\s\S]*?\*\/)/gm;
                const functions = /\b(COUNT|SUM|AVG|MIN|MAX|UPPER|LOWER|LENGTH|SUBSTR|TRIM|ROUND|FLOOR|CEIL|TO_DATE|TO_CHAR|NVL|DECODE|ROWNUM|SYSDATE)\s*\(/gi;
                
                let highlighted = code
                    .replace(comments, '<span class="text-slate-500 italic">$1</span>')
                    .replace(strings, '<span class="text-amber-300">$1</span>')
                    .replace(keywords, '<span class="text-cyan-400 font-semibold">$&</span>')
                    .replace(functions, '<span class="text-purple-400">$&</span>')
                    .replace(numbers, '<span class="text-orange-300">$1</span>');
                
                return highlighted;
            };
            
            const isSQL = language.toLowerCase() === 'sql';
            
            return !inline ? (
                <div className="relative group my-4 rounded-xl overflow-hidden border border-slate-700/50 bg-gradient-to-br from-[#0d1117] to-[#161b22] shadow-xl">
                    <div className="flex items-center justify-between px-4 py-2 bg-slate-800/80 border-b border-slate-700/50">
                        <div className="flex items-center gap-2">
                            <div className="flex gap-1">
                                <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></div>
                                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></div>
                            </div>
                            <span className="text-xs text-slate-400 font-mono uppercase tracking-wider">{language}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            {isSQL && (
                                <button
                                    onClick={() => handleExecuteSQL(codeContent)}
                                    disabled={executingSQL}
                                    className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 transition-colors px-2 py-1 rounded hover:bg-emerald-500/10 disabled:opacity-50"
                                    title="Exécuter la requête SQL"
                                >
                                    {executingSQL ? (
                                        <Loader2 size={12} className="animate-spin" />
                                    ) : (
                                        <Play size={12} />
                                    )}
                                    <span>Exécuter</span>
                                </button>
                            )}
                            <button
                                onClick={() => handleCopyCode(codeContent)}
                                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors px-2 py-1 rounded hover:bg-white/10"
                                title="Copier le code"
                            >
                                <Clipboard size={12} />
                                <span>Copier</span>
                            </button>
                        </div>
                    </div>
                    <div className="p-4 overflow-x-auto">
                        {isSQL ? (
                            <pre 
                                className="text-sm font-mono leading-relaxed"
                                dangerouslySetInnerHTML={{ __html: highlightSQL(codeContent) }}
                            />
                        ) : (
                            <code className={`${className} text-sm font-mono text-slate-200 leading-relaxed`} {...codeProps}>
                                {children}
                            </code>
                        )}
                    </div>
                </div>
            ) : (
                <code className="bg-slate-800/80 rounded px-1.5 py-0.5 text-sm font-mono text-cyan-300 border border-slate-700/50" {...codeProps}>
                    {children}
                </code>
            )
        }
    };


    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}>
            <div className={`flex max-w-[85%] md:max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4`}>

                <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center shadow-lg border border-white/10 ${isUser ? 'bg-gradient-to-br from-pack-blue to-pack-blue-dark' : 'bg-pack-gradient'}`}>
                    <span className="text-white font-bold text-sm">{isUser ? 'U' : 'P'}</span>
                </div>

                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} min-w-0`}>
                    <div className={`mt-1 text-xs font-semibold tracking-wide uppercase ${isUser ? 'text-pack-blue mr-2' : 'text-pack-blue ml-2'} mb-1`}>
                        {isUser ? 'Vous' : 'Pstral'}
                    </div>

                    <div className={`relative px-6 py-4 rounded-2xl shadow-xl border overflow-hidden ${isUser
                        ? 'bg-gradient-to-br from-indigo-600 to-purple-700 text-white rounded-tr-sm border-indigo-500/30'
                        : 'bg-glass-surface backdrop-blur-md text-slate-200 rounded-tl-sm border-white/5'
                        }`}>
                        {!isUser && isThinking && <div className="absolute inset-0 shimmer opacity-20 pointer-events-none"></div>}

                        {isThinking ? (
                            <div className="flex items-center gap-3">
                                <div className="flex space-x-1.5 h-4 items-center">
                                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
                                </div>
                                <span className="text-sm text-emerald-300 font-medium animate-pulse">Réflexion en cours...</span>
                            </div>
                        ) : isUser ? (
                            <div className="flex flex-col gap-3">
                                {images && images.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mb-1">
                                        {images.map((img, i) => (
                                            <img key={i} src={`data:image/png;base64,${img}`} alt="User attachment" className="max-w-[200px] rounded-lg border-2 border-white/20 shadow-sm" />
                                        ))}
                                    </div>
                                )}
                                <div className="leading-relaxed">{content}</div>
                            </div>
                        ) : (
                            <div className="prose prose-invert prose-p:leading-relaxed prose-pre:bg-[#0d1117] prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl max-w-none">
                                <Markdown components={components}>{content}</Markdown>
                            </div>
                        )}
                    </div>

                    {!isUser && !isThinking && (
                        <div className="flex gap-1 mt-2 ml-2">
                            <button
                                onClick={handleCopyMessage}
                                className="p-1.5 text-slate-500 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                                title="Copier le message"
                            >
                                <Copy size={14} />
                            </button>
                            {isLastAssistantMessage && onRegenerate && (
                                <button
                                    onClick={onRegenerate}
                                    className="p-1.5 text-slate-500 hover:text-blue-400 hover:bg-white/5 rounded-lg transition-all"
                                    title="Régénérer la réponse"
                                >
                                    <RefreshCw size={14} />
                                </button>
                            )}
                            <button
                                onClick={() => onFeedback('like')}
                                className="p-1.5 text-slate-500 hover:text-emerald-400 hover:bg-white/5 rounded-lg transition-all"
                                title="J'aime"
                            >
                                <ThumbsUp size={14} />
                            </button>
                            <button
                                onClick={() => onFeedback('dislike')}
                                className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-white/5 rounded-lg transition-all"
                                title="Je n'aime pas"
                            >
                                <ThumbsDown size={14} />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            <SQLResultsModal
                isOpen={sqlModalOpen}
                onClose={() => setSqlModalOpen(false)}
                results={sqlResults}
                query={currentQuery}
            />
        </div>
    );
};


export default MessageBubble;
