/**
 * HistoryChart — line chart showing past AQI data from the database.
 */

import { useState, useEffect, useCallback } from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { fetchHistory } from "../services/api";

function HistoryTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
        <div className="rounded-lg bg-slate-800 border border-slate-700/60 px-3 py-2 shadow-xl text-xs">
            <p className="font-semibold text-white">{label}</p>
            <p className="mt-1 text-cyan-400 font-mono">
                AQI: {d.aqi_value} — {d.aqi_category || "N/A"}
            </p>
        </div>
    );
}

export default function HistoryChart({ cities, selectedCity }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [hours, setHours] = useState(24);

    const city = selectedCity && selectedCity !== "all" ? selectedCity : cities?.[0] || null;

    const loadHistory = useCallback(async () => {
        if (!city) return;
        setLoading(true);
        try {
            const result = await fetchHistory(city, "pm25", hours);
            setHistory(result.data || []);
        } catch {
            setHistory([]);
        } finally {
            setLoading(false);
        }
    }, [city, hours]);

    useEffect(() => {
        loadHistory();
    }, [loadHistory]);

    if (!city) return null;

    // Format data for chart
    const chartData = history.map((item) => {
        const dt = new Date(item.recorded_at);
        return {
            ...item,
            label: dt.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
        };
    });

    return (
        <section className="dashboard-section">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    📊 Historical AQI Trend
                    <span className="ml-2 text-slate-600 normal-case font-normal">
                        {city} · PM2.5
                    </span>
                </h2>
                <div className="flex gap-1.5">
                    {[6, 12, 24, 48, 72].map((h) => (
                        <button
                            key={h}
                            onClick={() => setHours(h)}
                            className={`rounded-md px-2.5 py-1 text-[11px] font-medium transition ${hours === h
                                    ? "bg-cyan-600 text-white"
                                    : "bg-slate-800/60 text-slate-400 hover:bg-slate-700/60 border border-slate-700/40"
                                }`}
                        >
                            {h}h
                        </button>
                    ))}
                </div>
            </div>

            <div className="rounded-2xl bg-slate-800/50 border border-slate-700/40 p-4 sm:p-5">
                {loading ? (
                    <div className="skeleton h-48 rounded-xl" />
                ) : chartData.length === 0 ? (
                    <div className="py-16 text-center">
                        <p className="text-slate-500 text-sm">
                            No historical data yet. Data accumulates as the system runs.
                        </p>
                        <p className="text-slate-600 text-xs mt-1">
                            Each API refresh stores measurements in the database.
                        </p>
                    </div>
                ) : (
                    <>
                        <ResponsiveContainer width="100%" height={220}>
                            <AreaChart data={chartData} margin={{ top: 8, right: 12, left: -16, bottom: 4 }}>
                                <defs>
                                    <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.3} />
                                        <stop offset="100%" stopColor="#22d3ee" stopOpacity={0.02} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis
                                    dataKey="label"
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
                                <Tooltip content={<HistoryTooltip />} />
                                <Area
                                    type="monotone"
                                    dataKey="aqi_value"
                                    stroke="#22d3ee"
                                    strokeWidth={2}
                                    fill="url(#aqiGradient)"
                                    dot={{ r: 2.5, fill: "#22d3ee", stroke: "none" }}
                                    activeDot={{ r: 5, stroke: "#22d3ee", strokeWidth: 2, fill: "#0f172a" }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>

                        <p className="text-[11px] text-slate-600 mt-2 text-right">
                            {chartData.length} data points · Last {hours} hours
                        </p>
                    </>
                )}
            </div>
        </section>
    );
}
