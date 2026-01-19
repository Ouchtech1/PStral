import { useState, useEffect } from 'react';
import ChatInterface from './components/Chat/ChatInterface';
import Sidebar from './components/Layout/Sidebar';
import ModeSelectionModal from './components/UI/ModeSelectionModal';
import LoginPage from './components/Auth/LoginPage';
import { useAuth } from './contexts/AuthContext';
import { Loader2 } from 'lucide-react';

const CHAT_KEY = 'ministral_chat_';
const INDEX_KEY = 'ministral_chat_index';

// Loading component
const LoadingScreen = () => (
    <div className="h-screen bg-cosmic-void bg-cosmic-gradient flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
            <Loader2 size={40} className="text-pack-blue animate-spin" />
            <p className="text-slate-400">Chargement...</p>
        </div>
    </div>
);

// Main authenticated app content
const AuthenticatedApp = () => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [mode, setMode] = useState(null);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);

    // Load session list on mount
    useEffect(() => {
        const loadSessions = () => {
            try {
                const index = JSON.parse(localStorage.getItem(INDEX_KEY) || '[]');
                setSessions(index);
            } catch (e) {
                console.error("Failed to load chat history", e);
                setSessions([]);
            }
        };
        loadSessions();
    }, []);

    const createNewSession = (selectedMode) => {
        const newId = Date.now().toString();
        const newSession = {
            id: newId,
            mode: selectedMode,
            title: `Nouvelle discussion ${selectedMode}`,
            timestamp: Date.now()
        };

        const updatedSessions = [newSession, ...sessions];
        localStorage.setItem(INDEX_KEY, JSON.stringify(updatedSessions));
        setSessions(updatedSessions);
        localStorage.setItem(CHAT_KEY + newId, JSON.stringify([]));
        setCurrentSessionId(newId);
        setMode(selectedMode);
    };

    const handleModeSelect = (selectedMode) => {
        createNewSession(selectedMode);
    };

    const handleNewChatClick = () => {
        setCurrentSessionId(null);
        setMode(null);
    };

    const handleSelectSession = (sessionId) => {
        const session = sessions.find(s => s.id === sessionId);
        if (session) {
            setMode(session.mode);
            setCurrentSessionId(sessionId);
        }
    };

    const handleDeleteSession = (e, sessionId) => {
        e.stopPropagation();
        const updatedSessions = sessions.filter(s => s.id !== sessionId);
        localStorage.setItem(INDEX_KEY, JSON.stringify(updatedSessions));
        localStorage.removeItem(CHAT_KEY + sessionId);

        setSessions(updatedSessions);
        if (currentSessionId === sessionId) {
            setCurrentSessionId(null);
            setMode(null);
        }
    };

    const handleUpdateSessionTitle = (sessionId, newTitle) => {
        const updatedSessions = sessions.map(s => 
            s.id === sessionId ? { ...s, title: newTitle } : s
        );
        localStorage.setItem(INDEX_KEY, JSON.stringify(updatedSessions));
        setSessions(updatedSessions);
    };

    const handleImportChat = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (!data.messages || !Array.isArray(data.messages) || !data.mode) {
                    alert("Format de fichier invalide.");
                    return;
                }

                const newId = Date.now().toString();
                const newSession = {
                    id: newId,
                    mode: data.mode,
                    title: data.title || `Discussion ${data.mode} Importée`,
                    timestamp: Date.now()
                };

                const updatedSessions = [newSession, ...sessions];
                localStorage.setItem(INDEX_KEY, JSON.stringify(updatedSessions));
                localStorage.setItem(CHAT_KEY + newId, JSON.stringify(data.messages));

                setSessions(updatedSessions);
                setCurrentSessionId(newId);
                setMode(data.mode);
            } catch (err) {
                console.error("Import failed", err);
                alert("Échec de l'importation.");
            }
        };
        reader.readAsText(file);
    };

    return (
        <div className="flex h-screen bg-cosmic-void bg-cosmic-gradient text-starlight font-sans overflow-hidden">
            {/* Sidebar */}
            <div className={`${sidebarOpen ? 'w-[280px]' : 'w-0'} transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)] flex-shrink-0 overflow-hidden relative z-10`}>
                <Sidebar
                    onNewChat={handleNewChatClick}
                    sessions={sessions}
                    currentSessionId={currentSessionId}
                    onSelectSession={handleSelectSession}
                    onDeleteSession={handleDeleteSession}
                    onImportChat={handleImportChat}
                />
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-full relative z-0">
                {/* Header / Toggle */}
                <div className="absolute top-4 left-4 z-20">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2.5 rounded-xl bg-glass-surface hover:bg-white/10 text-slate-400 hover:text-white transition-all border border-glass-border hover:border-white/20 shadow-lg backdrop-blur-md"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                    </button>
                </div>

                {currentSessionId ? (
                    <ChatInterface
                        key={currentSessionId}
                        mode={mode}
                        sessionId={currentSessionId}
                        onUpdateTitle={(title) => handleUpdateSessionTitle(currentSessionId, title)}
                    />
                ) : (
                    <ModeSelectionModal onSelectMode={handleModeSelect} />
                )}
            </div>
        </div>
    );
};

// Root App component - only handles auth state
function App() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return <LoadingScreen />;
    }

    if (!isAuthenticated) {
        return <LoginPage />;
    }

    return <AuthenticatedApp />;
}

export default App;
