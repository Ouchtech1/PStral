// Classes CSS communes pour une meilleure lisibilité

export const btn = {
    base: "rounded-full transition-all duration-300 flex-shrink-0",
    icon: "p-3.5 mb-0.5 shadow-lg",
    primary: "bg-gradient-to-r from-nebula-blue to-nebula-purple hover:scale-105",
    danger: "bg-red-500 hover:bg-red-600 hover:scale-105",
    disabled: "bg-slate-700/50 text-slate-500 cursor-not-allowed",
    ghost: "p-1.5 text-slate-500 hover:bg-white/5 rounded-lg"
};

export const input = {
    base: "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pack-blue/50 transition-all"
};

export const card = {
    glass: "bg-glass-surface backdrop-blur-md border border-white/10 rounded-2xl shadow-lg"
};

export const text = {
    label: "block text-sm font-medium text-slate-300 mb-1.5",
    muted: "text-slate-400 text-sm"
};

