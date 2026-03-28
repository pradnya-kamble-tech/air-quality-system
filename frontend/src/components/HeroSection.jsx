/**
 * HeroSection — daily insight headline + key stats at the top.
 */

export default function HeroSection({ dailyInsight, stats, alertCount }) {
    return (
        <section id="hero-section" className="mb-8">
            {/* Daily Insight */}
            <div className="glass-card px-6 py-5 mb-5">
                <p className="text-[11px] uppercase tracking-widest text-cyan-400/70 font-semibold mb-2">
                    💡 Daily Insight
                </p>
                <p className="text-base sm:text-lg font-medium text-slate-200 leading-relaxed animate-fade-in-up">
                    {dailyInsight || "Analyzing air quality data across India..."}
                </p>
            </div>

            {/* Quick Stats Row */}
            {stats && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <QuickStat
                        label="Avg AQI"
                        value={stats.avgAqi ?? "—"}
                        color={stats.avgAqi <= 100 ? "#34d399" : stats.avgAqi <= 200 ? "#fbbf24" : "#f87171"}
                    />
                    <QuickStat
                        label="Worst City"
                        value={stats.worstCity}
                        sub={`AQI ${stats.worstAqi ?? "—"}`}
                        color={stats.worstColor}
                    />
                    <QuickStat
                        label="Cities Monitored"
                        value={stats.cities}
                        color="#22d3ee"
                    />
                    <QuickStat
                        label="Active Alerts"
                        value={alertCount}
                        color={alertCount > 0 ? "#fb7185" : "#34d399"}
                    />
                </div>
            )}
        </section>
    );
}

function QuickStat({ label, value, sub, color }) {
    return (
        <div className="glass-card px-4 py-3 text-center">
            <p className="text-[10px] uppercase tracking-wider text-slate-500 font-medium mb-1">{label}</p>
            <p className="text-xl font-black tabular-nums animate-count" style={{ color }}>
                {value}
            </p>
            {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
        </div>
    );
}
