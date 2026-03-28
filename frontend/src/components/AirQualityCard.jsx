/**
 * AirQualityCard — premium card with decision, score, trend, and health advice.
 */

import ScoreGauge from "./ScoreGauge";

const GLOW_MAP = {
    "#10b981": "glow-green",
    "#facc15": "glow-yellow",
    "#fb923c": "glow-orange",
    "#ef4444": "glow-red",
    "#a78bfa": "glow-purple",
    "#991b1b": "glow-maroon",
};

const TREND_ICONS = {
    increasing: { icon: "▲", color: "#f87171", label: "Rising", cls: "trend-up" },
    decreasing: { icon: "▼", color: "#34d399", label: "Falling", cls: "trend-down" },
    stable: { icon: "●", color: "#94a3b8", label: "Stable", cls: "" },
};

const DECISION_CLS = {
    yes: "decision-yes",
    limited: "decision-limited",
    no: "decision-no",
};

export default function AirQualityCard({
    city, station, pollutant, value, unit, aqi_value, aqi_category, aqi_color,
    health_advice, decision_status, decision_label, decision_emoji, score, trend,
    index = 0,
}) {
    const glowClass = GLOW_MAP[aqi_color] || "";
    const trendInfo = TREND_ICONS[trend] || TREND_ICONS.stable;
    const decisionCls = DECISION_CLS[decision_status] || "";

    return (
        <div
            className={`glass-card ${glowClass} p-5 animate-fade-in-up`}
            style={{
                animationDelay: `${index * 80}ms`,
                borderTopColor: aqi_color,
                borderTopWidth: "2px",
            }}
        >
            {/* ── Row 1: Header ── */}
            <div className="flex items-start justify-between mb-3">
                <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-bold text-white truncate">{city}</h3>
                    <p className="text-[11px] text-slate-500 truncate">📍 {station}</p>
                </div>
                {/* Decision Badge */}
                {decision_status && (
                    <span className={`shrink-0 inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-bold ${decisionCls}`}>
                        {decision_emoji} {decision_label}
                    </span>
                )}
            </div>

            {/* ── Row 2: AQI + Score + Trend ── */}
            <div className="flex items-center gap-4 mb-4">
                {/* AQI Value */}
                <div className="flex-1">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">AQI</p>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black tabular-nums animate-count" style={{ color: aqi_color }}>
                            {aqi_value ?? "—"}
                        </span>
                        {/* Trend */}
                        <span className={`text-xs font-bold ${trendInfo.cls}`} style={{ color: trendInfo.color }}>
                            {trendInfo.icon} {trendInfo.label}
                        </span>
                    </div>
                    <p className="text-[11px] font-medium mt-0.5" style={{ color: aqi_color }}>
                        {aqi_category}
                    </p>
                </div>

                {/* Score Gauge */}
                {score != null && <ScoreGauge score={score} size={64} />}
            </div>

            {/* ── Row 3: Raw Data ── */}
            <div className="flex items-center gap-3 mb-3 rounded-lg bg-slate-900/40 px-3 py-2 text-xs">
                <span className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2 py-0.5 font-mono text-[11px] text-cyan-300 border border-slate-700/40">
                    {pollutant.toUpperCase()}
                </span>
                <span className="text-slate-300 font-medium tabular-nums">
                    {value} <span className="text-slate-500">{unit}</span>
                </span>
            </div>

            {/* ── Row 4: Health Advice ── */}
            {health_advice && (
                <div className="rounded-lg bg-slate-900/30 border border-slate-700/20 px-3 py-2">
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                        {health_advice}
                    </p>
                </div>
            )}
        </div>
    );
}
