import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ error, errorInfo });
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="fixed inset-0 bg-slate-900 text-red-500 p-10 font-mono overflow-auto z-[9999]">
                    <h1 className="text-2xl font-bold mb-4">Something went wrong (Frontend Crash)</h1>
                    <div className="bg-slate-800 p-4 rounded mb-4 border border-red-500/30">
                        <p className="font-bold">{this.state.error && this.state.error.toString()}</p>
                    </div>
                    <details className="whitespace-pre-wrap text-sm text-slate-400">
                        {this.state.errorInfo && this.state.errorInfo.componentStack}
                    </details>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Reload Application
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
