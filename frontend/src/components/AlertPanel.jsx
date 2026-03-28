/**
 * AlertPanel — scrollable list of all active air quality alerts.
 */

const SEVERITY_CONFIG = {
    critical: {
        bg: "bg-rose-950/40",
        border: "border-rose-500/30",
        dot: "bg-rose-500",
        text: "text-rose-300",
        label: "Critical",
    },
    high: {
        bg: "bg-orange-950/30",
        border: "border-orange-500/25",
        dot: "bg-orange-500",
        text: "text-orange-300",
        label: "High",
    },
    medium: {
        bg: "bg-yellow-950/20",
        border: "border-yellow-600/20",
        dot: "bg-yellow-500",
        text: "text-yellow-300",
        label: "Medium",
    },
};

export default function AlertPanel({ alerts }) {
    if (!alerts?.length) return null;

    return (
        <section id="alerts-section" className="dashboard-section">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                🚨 Air Quality Alerts
                <span className="ml-2 text-rose-400 font-bold">{alerts.length}</span>
            </h2>

            <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1 scrollbar-thin">
                {alerts.map((alert, idx) => {
                    const cfg = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium;
                    return (
                        <div
                            key={`${alert.city}-${alert.pollutant}-${alert.type}-${idx}`}
                            className={`rounded-xl border ${cfg.border} ${cfg.bg} px-4 py-3 flex items-start gap-3 transition-all duration-300 hover:bg-slate-800/40`}
                        >
                            {/* Severity dot */}
                            <span className={`mt-1 shrink-0 h-2.5 w-2.5 rounded-full ${cfg.dot}`} />

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-sm font-bold text-white">{alert.city}</span>
                                    <span className={`text-[10px] font-semibold uppercase tracking-wider ${cfg.text}`}>
                                        {cfg.label}
                                    </span>
                                    <span className="rounded-full bg-slate-700/50 border border-slate-600/40 px-1.5 py-0.5 text-[9px] text-slate-400 uppercase font-medium">
                                        {alert.type === "prediction" ? "forecast" : "live"}
                                    </span>
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                    {alert.message}
                                </p>
                                <p className="text-[10px] text-slate-500 mt-1">
                                    {alert.pollutant.toUpperCase()} · AQI <span className={`font-bold ${cfg.text}`}>{alert.aqi}</span>
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </section>
    );
}
