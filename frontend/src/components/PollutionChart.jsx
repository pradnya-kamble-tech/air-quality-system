/**
 * PollutionChart — bar chart comparing AQI values across cities.
 */

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";

function CustomTooltip({ active, payload }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
        <div className="rounded-lg bg-slate-800 border border-slate-700/60 px-3 py-2 shadow-xl text-xs">
            <p className="font-semibold text-white">{d.city}</p>
            <p className="text-slate-400">{d.station}</p>
            <p className="mt-1 font-mono" style={{ color: d.aqi_color || "#22d3ee" }}>
                AQI: {d.aqi_value ?? "N/A"} — {d.aqi_category || "Unknown"}
            </p>
            <p className="text-slate-500">
                {d.pollutant.toUpperCase()}: {d.value} {d.unit}
            </p>
        </div>
    );
}

export default function PollutionChart({ data }) {
    if (!data.length) return null;

    const chartData = data.map((d) => ({
        ...d,
        label: d.city,
        aqiDisplay: d.aqi_value ?? 0,
    }));

    return (
        <section id="chart-section" className="dashboard-section">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">
                📊 AQI City Comparison
            </h2>
            <div className="rounded-2xl bg-slate-800/50 border border-slate-700/40 p-4 sm:p-6">
                <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={chartData} margin={{ top: 8, right: 8, left: -10, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis
                            dataKey="label"
                            tick={{ fill: "#94a3b8", fontSize: 12 }}
                            axisLine={{ stroke: "#475569" }}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fill: "#94a3b8", fontSize: 12 }}
                            axisLine={{ stroke: "#475569" }}
                            tickLine={false}
                            domain={[0, "auto"]}
                            label={{
                                value: "AQI",
                                angle: -90,
                                position: "insideLeft",
                                offset: 20,
                                style: { fill: "#64748b", fontSize: 11 },
                            }}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(148, 163, 184, 0.08)" }} />
                        <Bar dataKey="aqiDisplay" radius={[6, 6, 0, 0]} maxBarSize={56}>
                            {chartData.map((entry, idx) => (
                                <Cell
                                    key={idx}
                                    fill={entry.aqi_color || "#94a3b8"}
                                    fillOpacity={0.85}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </section>
    );
}
