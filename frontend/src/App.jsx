import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import ChatInterface from './components/Chat/ChatInterface';
import Sidebar from './components/Layout/Sidebar';
import ModeSelectionModal from './components/UI/ModeSelectionModal';
import LoginPage from './components/Auth/LoginPage';
import { useAuth } from './contexts/AuthContext';

const LoadingScreen = () => (
    <div className="h-screen bg-pack-bg-light bg-pack-bg-gradient flex items-center justify-center">
        <Loader2 size={40} className="text-pack-blue animate-spin" />
    </div>
);

const AuthenticatedApp = () => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [mode, setMode] = useState(null);
    const [dialogueVersion, setDialogueVersion] = useState(0);

    const startMode = (selectedMode) => {
        setMode(selectedMode);
        setDialogueVersion((version) => version + 1);
    };

    const newDialogue = () => {
        setMode(null);
        setDialogueVersion((version) => version + 1);
    };

    return (
        <div className="flex h-screen bg-pack-bg-light bg-pack-bg-gradient text-white font-sans overflow-hidden">
            <div className={(sidebarOpen ? 'w-[280px]' : 'w-0') + ' transition-all duration-500 flex-shrink-0 overflow-hidden'}>
                <Sidebar onNewChat={newDialogue} mode={mode} />
            </div>
            <main className="flex-1 flex flex-col h-full relative">
                <div className="absolute top-4 left-4 z-20">
                    <button
                        onClick={() => setSidebarOpen((open) => !open)}
                        className="p-2.5 rounded-xl bg-glass-surface text-slate-400 hover:text-white border border-glass-border"
                        aria-label="Afficher ou masquer le panneau"
                    >
                        ☰
                    </button>
                </div>
                {mode ? (
                    <ChatInterface key={mode + '-' + dialogueVersion} mode={mode} />
                ) : (
                    <ModeSelectionModal onSelectMode={startMode} />
                )}
            </main>
        </div>
    );
};

function App() {
    const { isAuthenticated, loading, sessionVersion } = useAuth();
    if (loading) return <LoadingScreen />;
    if (!isAuthenticated) return <LoginPage />;
    return <AuthenticatedApp key={sessionVersion} />;
}

export default App;
