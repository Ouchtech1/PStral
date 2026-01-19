import React from 'react';
import { X, Download, AlertTriangle, CheckCircle, Table2 } from 'lucide-react';

const SQLResultsModal = ({ isOpen, onClose, results, query }) => {
    if (!isOpen) return null;

    const handleExportCSV = () => {
        if (!results?.rows?.length) return;
        
        const headers = results.columns.join(',');
        const rows = results.rows.map(row => 
            results.columns.map(col => {
                const val = row[col];
                // Escape quotes and wrap in quotes if contains comma
                if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
                    return `"${val.replace(/"/g, '""')}"`;
                }
                return val ?? '';
            }).join(',')
        ).join('\n');
        
        const csv = `${headers}\n${rows}`;
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pstral-query-results-${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-cosmic-void/90 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="glass-panel w-full max-w-5xl max-h-[85vh] rounded-2xl shadow-2xl border border-white/10 flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5">
                    <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${results?.success ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                            {results?.success ? (
                                <Table2 size={20} className="text-emerald-400" />
                            ) : (
                                <AlertTriangle size={20} className="text-red-400" />
                            )}
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white">
                                Résultats de la requête
                            </h3>
                            <p className="text-sm text-slate-400">
                                {results?.success 
                                    ? `${results.row_count} ligne(s) retournée(s)`
                                    : 'Erreur lors de l\'exécution'
                                }
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        {results?.success && results?.rows?.length > 0 && (
                            <button
                                onClick={handleExportCSV}
                                className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            >
                                <Download size={16} />
                                Exporter CSV
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Query preview */}
                <div className="px-6 py-3 bg-slate-900/50 border-b border-white/5">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Requête exécutée</p>
                    <pre className="text-sm text-cyan-300 font-mono overflow-x-auto whitespace-pre-wrap">
                        {query}
                    </pre>
                </div>

                {/* Results */}
                <div className="flex-1 overflow-auto p-6">
                    {results?.warning && (
                        <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg flex items-center gap-3">
                            <AlertTriangle size={18} className="text-amber-400 flex-shrink-0" />
                            <p className="text-sm text-amber-200">{results.warning}</p>
                        </div>
                    )}

                    {results?.error && (
                        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                            <p className="text-sm text-red-300">{results.error}</p>
                        </div>
                    )}

                    {results?.success && results?.rows?.length > 0 && (
                        <div className="overflow-x-auto rounded-xl border border-white/10">
                            <table className="w-full text-sm">
                                <thead className="bg-slate-800/80">
                                    <tr>
                                        {results.columns.map((col, idx) => (
                                            <th 
                                                key={idx}
                                                className="px-4 py-3 text-left font-semibold text-slate-300 border-b border-white/10 whitespace-nowrap"
                                            >
                                                {col}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {results.rows.map((row, rowIdx) => (
                                        <tr key={rowIdx} className="hover:bg-white/5 transition-colors">
                                            {results.columns.map((col, colIdx) => (
                                                <td 
                                                    key={colIdx}
                                                    className="px-4 py-3 text-slate-200 whitespace-nowrap"
                                                >
                                                    {row[col] !== null && row[col] !== undefined 
                                                        ? String(row[col]) 
                                                        : <span className="text-slate-500 italic">NULL</span>
                                                    }
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {results?.success && results?.rows?.length === 0 && (
                        <div className="text-center py-12">
                            <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Table2 size={32} className="text-slate-500" />
                            </div>
                            <p className="text-slate-400">Aucun résultat retourné</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SQLResultsModal;

