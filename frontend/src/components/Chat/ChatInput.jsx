import React, { useState, useRef, useEffect } from 'react';
import { SendHorizontal, Paperclip, X, FileText, Image as ImageIcon, Loader2, Square, AlertTriangle } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString();

const MAX_FILE_CONTENT_LENGTH = 3000;

const SendButton = ({ isGenerating, onStop, onSend, disabled }) => {
    const base = "p-3.5 mb-0.5 rounded-full text-white shadow-lg flex-shrink-0 transition-all duration-300";
    
    if (isGenerating) {
        return (
            <button onClick={onStop} className={`${base} bg-red-500 hover:bg-red-600 hover:scale-105`} title="Arrêter">
                <Square size={20} fill="currentColor" />
            </button>
        );
    }
    
    return (
        <button
            onClick={onSend}
            disabled={disabled}
            className={`${base} ${disabled ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed' : 'bg-gradient-to-r from-nebula-blue to-nebula-purple hover:scale-105'}`}
        >
            <SendHorizontal size={20} />
        </button>
    );
};

const ChatInput = ({ onSend, disabled, isGenerating = false, onStop }) => {
    const [input, setInput] = useState('');
    const [attachment, setAttachment] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const textareaRef = useRef(null);
    const fileInputRef = useRef(null);

    const truncateContent = (content) => {
        if (content.length <= MAX_FILE_CONTENT_LENGTH) {
            return { content, truncated: false };
        }
        return {
            content: content.substring(0, MAX_FILE_CONTENT_LENGTH) + '\n\n[... contenu tronqué pour optimiser le traitement ...]',
            truncated: true
        };
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if ((!input.trim() && !attachment) || disabled || isProcessing) return;

        let messagePayload = { content: input, images: [] };

        if (attachment) {
            if (attachment.type === 'image') {
                messagePayload.images = [attachment.base64];
                if (!input.trim()) messagePayload.content = "Analysez cette image.";
            } else {
                messagePayload.content = `${input}\n\n--- Fichier: ${attachment.name} ---\n${attachment.content}`;
            }
        }

        onSend(messagePayload);
        setInput('');
        setAttachment(null);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsProcessing(true);
        try {
            if (file.type === 'application/pdf') {
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                let fullText = "";
                const maxPages = Math.min(pdf.numPages, 5);
                
                for (let i = 1; i <= maxPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    fullText += `\n--- Page ${i} ---\n${textContent.items.map(item => item.str).join(' ')}`;
                }

                const { content, truncated } = truncateContent(fullText.trim());
                setAttachment({ name: file.name, content, type: 'text', truncated });

            } else if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const result = event.target.result;
                    setAttachment({
                        name: file.name,
                        content: "[Image]",
                        type: 'image',
                        base64: result.split(',')[1],
                        preview: result
                    });
                    setIsProcessing(false);
                };
                reader.readAsDataURL(file);
                return;
            } else {
                const text = await file.text();
                const { content, truncated } = truncateContent(text);
                setAttachment({ name: file.name, content, type: 'text', truncated });
            }
        } catch (err) {
            console.error("Erreur fichier:", err);
            alert("Échec du traitement: " + err.message);
        } finally {
            if (!file.type.startsWith('image/')) setIsProcessing(false);
        }
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [input]);

    return (
        <div className="max-w-3xl w-full mx-auto p-4 flex flex-col items-center">

            {attachment && (
                <div className="mb-3 flex items-center gap-3 bg-glass-surface backdrop-blur-md px-4 py-2 rounded-2xl border border-white/10 text-sm animate-slide-up shadow-lg">
                    {attachment.type === 'image' ? (
                        <div className="relative group overflow-hidden rounded-lg border border-white/10">
                            <img src={attachment.preview} alt="preview" className="w-10 h-10 object-cover" />
                            <div className="absolute inset-0 bg-black/50 hidden group-hover:flex items-center justify-center transition-all">
                                <ImageIcon size={14} className="text-white" />
                            </div>
                        </div>
                    ) : (
                        <div className="p-2 bg-nebula-blue/20 rounded-lg text-nebula-blue">
                            <FileText size={18} />
                        </div>
                    )}
                    <div className="flex flex-col max-w-[200px]">
                        <span className="text-slate-200 font-medium truncate">{attachment.name}</span>
                        <div className="flex items-center gap-1">
                        <span className="text-[10px] text-slate-400 uppercase tracking-wider">{attachment.type}</span>
                            {attachment.truncated && (
                                <span className="text-[10px] text-amber-400 flex items-center gap-0.5" title="Fichier tronqué pour optimiser le traitement">
                                    <AlertTriangle size={10} /> tronqué
                                </span>
                            )}
                        </div>
                    </div>

                    <button
                        onClick={() => { setAttachment(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
                        className="ml-2 p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded-full text-slate-400 transition-all"
                    >
                        <X size={14} />
                    </button>
                </div>
            )}

            {isProcessing && (
                <div className="mb-2 text-xs text-nebula-blue bg-nebula-blue/10 px-3 py-1 rounded-full border border-nebula-blue/20 flex items-center gap-2 animate-pulse">
                    <Loader2 size={12} className="animate-spin" /> Analyse du fichier en cours...
                </div>
            )}

            <div className={`
                relative w-full flex items-end gap-2 p-2 rounded-[2rem] shadow-2xl transition-all duration-300
                bg-cosmic-night/80 backdrop-blur-xl border border-glass-border
                focus-within:ring-2 focus-within:ring-nebula-purple/50 focus-within:border-nebula-purple/50
                hover:border-white/20
            `}>
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".txt,.sql,.csv,.json,.md,.py,.js,.pdf,.png,.jpg,.jpeg,.gif,.webp"
                />

                <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={disabled || isProcessing}
                    className="p-3.5 mb-0.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-full transition-all flex-shrink-0"
                    title="Joindre un fichier"
                >
                    <Paperclip size={20} />
                </button>

                <textarea
                    ref={textareaRef}
                    rows={1}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Posez votre question à Pstral..."
                    disabled={disabled || isProcessing}
                    className="w-full bg-transparent border-none focus:ring-0 resize-none text-slate-200 placeholder-slate-500 py-4 px-2 max-h-[200px] overflow-y-auto leading-relaxed scrollbar-thin scrollbar-thumb-white/10"
                    style={{ minHeight: '52px' }}
                />

                <SendButton
                    isGenerating={isGenerating}
                    onStop={onStop}
                    onSend={handleSubmit}
                    disabled={(!input.trim() && !attachment) || disabled || isProcessing}
                />
            </div>

            <div className="mt-4 flex items-center gap-2 text-[10px] text-slate-500 font-medium tracking-wide uppercase opacity-70">
                <span className="w-1.5 h-1.5 rounded-full bg-pack-blue animate-pulse"></span>
                Pack Solutions • Usage Interne Uniquement
            </div>

        </div>
    );
};

export default ChatInput;
