/**
 * ForecastChart — line chart showing AQI predictions per city.
 */

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
        <div className="rounded-lg bg-slate-800 border border-slate-700/60 px-3 py-2 shadow-xl text-xs">
            <p className="font-semibold text-white">{label}</p>
            <p className="mt-1 font-mono" style={{ color: d.color }}>
                AQI: {d.aqi} — {d.category}
            </p>
        </div>
    );
}

function CityForecast({ forecast }) {
    // Build chart data: start with "Now" point, then predictions
    const chartData = [
        {
            time: "Now",
            aqi: forecast.current_aqi,
            category: forecast.current_category,
            color: forecast.current_color,
            isCurrent: true,
        },
        ...forecast.predictions.map((p) => ({
            time: `+${p.hour_offset}h`,
            aqi: p.aqi,
            category: p.category,
            color: p.color,
            isCurrent: false,
        })),
    ];

    // Use last prediction color for the line
    const lineColor = forecast.current_color || "#22d3ee";

    return (
        <div className="rounded-2xl bg-slate-800/50 border border-slate-700/40 p-4 sm:p-5">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div>
                    <h3 className="text-base font-bold text-white">{forecast.city}</h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                        {forecast.pollutant.toUpperCase()} · {forecast.station}
                    </p>
                </div>
                <span
                    className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold"
                    style={{
                        backgroundColor: `${forecast.current_color}20`,
                        color: forecast.current_color,
                        borderColor: `${forecast.current_color}40`,
                    }}
                >
                    Now: {forecast.current_aqi}
                </span>
            </div>

            {/* Chart */}
            <ResponsiveContainer width="100%" height={180}>
                <LineChart data={chartData} margin={{ top: 8, right: 12, left: -16, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis
                        dataKey="time"
                        tick={{ fill: "#94a3b8", fontSize: 11 }}
                        axisLine={{ stroke: "#475569" }}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: "#94a3b8", fontSize: 11 }}
                        axisLine={{ stroke: "#475569" }}
                        tickLine={false}
                        domain={[0, "auto"]}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine
                        y={forecast.current_aqi}
                        stroke="#475569"
                        strokeDasharray="3 3"
                        label={{
                            value: "Current",
                            position: "right",
                            fill: "#64748b",
                            fontSize: 10,
                        }}
                    />
                    <Line
                        type="monotone"
                        dataKey="aqi"
                        stroke={lineColor}
                        strokeWidth={2.5}
                        strokeDasharray="8 4"
                        dot={(props) => {
                            const { cx, cy, payload } = props;
                            if (payload.isCurrent) {
                                return (
                                    <circle
                                        key="current"
                                        cx={cx}
                                        cy={cy}
                                        r={5}
                                        fill={lineColor}
                                        stroke="#0f172a"
                                        strokeWidth={2}
                                    />
                                );
                            }
                            return (
                                <circle
                                    key={payload.time}
                                    cx={cx}
                                    cy={cy}
                                    r={3}
                                    fill={payload.color || lineColor}
                                    stroke="none"
                                />
                            );
                        }}
                        activeDot={{ r: 5, stroke: lineColor, strokeWidth: 2, fill: "#0f172a" }}
                    />
                </LineChart>
            </ResponsiveContainer>

            {/* Prediction summary row */}
            <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
                {forecast.predictions.map((p) => (
                    <div
                        key={p.hour_offset}
                        className="flex-shrink-0 rounded-lg bg-slate-900/60 border border-slate-700/30 px-2.5 py-1.5 text-center min-w-[60px]"
                    >
                        <p className="text-[10px] text-slate-500">+{p.hour_offset}h</p>
                        <p className="text-sm font-bold tabular-nums" style={{ color: p.color }}>
                            {p.aqi}
                        </p>
                        <p className="text-[9px] text-slate-500 truncate" style={{ maxWidth: "60px" }}>
                            {p.category}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function ForecastChart({ predictions, selectedCity }) {
    // predictions is now an object: { data: Array, insight: String }
    const forecastData = predictions?.data || [];

    if (!forecastData.length) return null;

    // Filter by selected city if active
    const filtered =
        selectedCity && selectedCity !== "all"
            ? forecastData.filter((p) => p.city === selectedCity)
            : forecastData;

    if (!filtered.length) return null;

    return (
        <section id="forecast-section" className="dashboard-section">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">
                🔮 Air Quality Forecast
                <span className="ml-2 text-slate-600 normal-case font-normal">
                    Next 6 hours · ARIMA ML Model
                </span>
            </h2>
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-2">
                {filtered.map((f) => (
                    <CityForecast key={`${f.city}-${f.pollutant}`} forecast={f} />
                ))}
            </div>

            {predictions?.insight && (
                <div className="mt-5 flex items-start gap-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 p-4 shadow-lg shadow-cyan-900/10">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 text-xl border border-cyan-500/30">
                        🤖
                    </div>
                    <div>
                        <h4 className="text-[11px] font-bold text-cyan-400 uppercase tracking-widest mb-1">
                            ML Prediction Insight
                        </h4>
                        <p className="text-sm text-slate-200 leading-relaxed">
                            {predictions.insight}
                        </p>
                        <p className="text-[10px] text-slate-500 mt-2 italic">
                            *Analysis generated by analyzing current trends across all monitored stations.
                        </p>
                    </div>
                </div>
            )}
        </section>
    );
}

