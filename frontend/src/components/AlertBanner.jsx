/**
 * AlertBanner — prominent top banner for the most critical alert.
 */

const SEVERITY_STYLES = {
    critical: {
        bg: "bg-rose-950/80",
        border: "border-rose-500/50",
        icon: "🔴",
        text: "text-rose-200",
        badge: "bg-rose-500/30 text-rose-300 border-rose-500/40",
        pulse: true,
    },
    high: {
        bg: "bg-orange-950/70",
        border: "border-orange-500/40",
        icon: "🟠",
        text: "text-orange-200",
        badge: "bg-orange-500/30 text-orange-300 border-orange-500/40",
        pulse: true,
    },
    medium: {
        bg: "bg-yellow-950/60",
        border: "border-yellow-600/30",
        icon: "🟡",
        text: "text-yellow-200",
        badge: "bg-yellow-500/20 text-yellow-300 border-yellow-600/30",
        pulse: false,
    },
};

export default function AlertBanner({ alerts }) {
    if (!alerts?.length) return null;

    // Show the most critical alert
    const alert = alerts[0];
    const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.medium;

    return (
        <div
            id="alert-banner"
            className={`mb-6 rounded-xl border ${style.border} ${style.bg} backdrop-blur-sm px-4 py-3 flex items-center gap-3 transition-all duration-500`}
        >
            {/* Icon with optional pulse */}
            <span className="text-xl shrink-0">
                {style.pulse ? (
                    <span className="relative inline-flex">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-50">{style.icon}</span>
                        <span className="relative">{style.icon}</span>
                    </span>
                ) : (
                    style.icon
                )}
            </span>

            {/* Message */}
            <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${style.text} truncate`}>
                    {alert.message}
                </p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                    {alert.pollutant.toUpperCase()} · AQI {alert.aqi}
                </p>
            </div>

            {/* Severity + type badge */}
            <div className="flex items-center gap-2 shrink-0">
                <span className={`inline-flex rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${style.badge}`}>
                    {alert.severity}
                </span>
                <span className="rounded-full bg-slate-700/50 border border-slate-600/40 px-2 py-0.5 text-[10px] font-medium text-slate-400 uppercase">
                    {alert.type === "prediction" ? "forecast" : "live"}
                </span>
            </div>

            {/* Alert count */}
            {alerts.length > 1 && (
                <span className="shrink-0 rounded-full bg-slate-700/60 border border-slate-600/30 px-2 py-0.5 text-[10px] text-slate-400 font-medium">
                    +{alerts.length - 1} more
                </span>
            )}
        </div>
    );
}
