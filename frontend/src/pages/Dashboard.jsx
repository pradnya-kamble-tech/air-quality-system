import { useState, useEffect, useCallback, useMemo } from "react";
import { fetchAirQuality, fetchPredictions, fetchAlerts } from "../services/api";
import AirQualityCard from "../components/AirQualityCard";
import FilterBar from "../components/FilterBar";
import PollutionChart from "../components/PollutionChart";
import AqiLegend from "../components/AqiLegend";
import ForecastChart from "../components/ForecastChart";
import AlertBanner from "../components/AlertBanner";
import AlertPanel from "../components/AlertPanel";
import HeroSection from "../components/HeroSection";

const REFRESH_INTERVAL = 30_000;

function SkeletonCard() {
    return <div className="skeleton h-64 rounded-2xl" />;
}

export default function Dashboard() {
    const [data, setData] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [dailyInsight, setDailyInsight] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [selectedCity, setSelectedCity] = useState("all");
    const [selectedPollutant, setSelectedPollutant] = useState("all");

    const loadData = useCallback(async () => {
        try {
            const [aqResult, predResult, alertResult] = await Promise.all([
                fetchAirQuality(),
                fetchPredictions().catch(() => ({ data: [] })),
                fetchAlerts().catch(() => ({ alerts: [] })),
            ]);
            setData(aqResult.data || []);
            setDailyInsight(aqResult.daily_insight || "");
            setPredictions(predResult.data || []);
            setAlerts(alertResult.alerts || []);
            setError(null);
            setLastUpdate(new Date());
        } catch (err) {
            console.error("Fetch error:", err);
            setError("Unable to reach the Air Quality API. Make sure the backend is running.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadData();
        const id = setInterval(loadData, REFRESH_INTERVAL);
        return () => clearInterval(id);
    }, [loadData]);

    const cities = useMemo(() => [...new Set(data.map((d) => d.city))].sort(), [data]);
    const pollutants = useMemo(() => [...new Set(data.map((d) => d.pollutant))].sort(), [data]);

    const filteredData = useMemo(() => {
        return data.filter((d) => {
            if (selectedCity !== "all" && d.city !== selectedCity) return false;
            if (selectedPollutant !== "all" && d.pollutant !== selectedPollutant) return false;
            return true;
        });
    }, [data, selectedCity, selectedPollutant]);

    const stats = useMemo(() => {
        if (!filteredData.length) return null;
        const citySet = new Set(filteredData.map((d) => d.city));
        const aqiValues = filteredData.filter((d) => d.aqi_value != null);
        const avgAqi = aqiValues.length
            ? Math.round(aqiValues.reduce((s, d) => s + d.aqi_value, 0) / aqiValues.length)
            : null;
        const worst = aqiValues.length
            ? aqiValues.reduce((mx, d) => (d.aqi_value > mx.aqi_value ? d : mx), aqiValues[0])
            : null;
        return {
            cities: citySet.size,
            avgAqi,
            worstAqi: worst?.aqi_value ?? null,
            worstCity: worst?.city ?? "—",
            worstColor: worst?.aqi_color ?? "#fff",
        };
    }, [filteredData]);

    /* ── Loading ── */
    if (loading) {
        return (
            <div className="min-h-screen bg-animate px-4 py-8 sm:px-6 lg:px-10">
                <div className="mx-auto max-w-7xl">
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-2">🇮🇳 India Air Quality Monitor</h1>
                    <p className="text-sm text-slate-400 mb-10">Loading live data…</p>
                    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
                    </div>
                </div>
            </div>
        );
    }

    /* ── Error ── */
    if (error) {
        return (
            <div className="flex min-h-screen items-center justify-center p-6 bg-animate">
                <div className="glass-card max-w-md p-8 text-center">
                    <div className="text-4xl mb-4">⚠️</div>
                    <h2 className="text-lg font-semibold text-rose-400 mb-2">Connection Error</h2>
                    <p className="text-sm text-slate-400 mb-6">{error}</p>
                    <button onClick={loadData} className="rounded-lg bg-cyan-600 px-5 py-2 text-sm font-medium text-white hover:bg-cyan-500 active:scale-95 transition">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-animate px-4 py-8 sm:px-6 lg:px-10">
            <div className="mx-auto max-w-7xl">

                {/* ═══ Alert Banner ═══ */}
                <AlertBanner alerts={alerts} />

                {/* ═══ Header ═══ */}
                <header className="mb-6">
                    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
                        <div>
                            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                                🇮🇳 India Air Quality Monitor
                            </h1>
                            <p className="mt-1 text-sm text-slate-400">
                                Smart Air Quality Assistant &middot; Updates every 30s
                            </p>
                        </div>
                        {lastUpdate && (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-800/70 border border-slate-700/40 px-3 py-1 text-xs text-slate-400">
                                <span className="relative flex h-2 w-2">
                                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                                    <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                                </span>
                                {lastUpdate.toLocaleTimeString("en-IN")}
                            </span>
                        )}
                    </div>
                </header>

                {/* ═══ Hero: Daily Insight + Quick Stats ═══ */}
                <HeroSection dailyInsight={dailyInsight} stats={stats} alertCount={alerts.length} />

                {/* ═══ Filters ═══ */}
                <FilterBar
                    cities={cities}
                    pollutants={pollutants}
                    selectedCity={selectedCity}
                    selectedPollutant={selectedPollutant}
                    onCityChange={setSelectedCity}
                    onPollutantChange={setSelectedPollutant}
                />

                {/* ═══ Alerts Panel ═══ */}
                <AlertPanel alerts={alerts} />

                {/* ═══ AQI Legend ═══ */}
                <AqiLegend />

                {/* ═══ Charts ═══ */}
                <PollutionChart data={filteredData} />

                {/* ═══ Forecast ═══ */}
                <ForecastChart predictions={predictions} selectedCity={selectedCity} />

                {/* ═══ Station Cards ═══ */}
                <section className="dashboard-section">
                    <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">
                        🗂️ Monitoring Stations
                        {filteredData.length !== data.length && (
                            <span className="ml-2 text-cyan-400">({filteredData.length} of {data.length})</span>
                        )}
                    </h2>
                    {filteredData.length > 0 ? (
                        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                            {filteredData.map((item, idx) => (
                                <AirQualityCard key={`${item.station}-${item.pollutant}-${idx}`} {...item} index={idx} />
                            ))}
                        </div>
                    ) : (
                        <div className="glass-card py-16 text-center">
                            <p className="text-slate-500 text-sm">No data matches current filters.</p>
                            <button
                                onClick={() => { setSelectedCity("all"); setSelectedPollutant("all"); }}
                                className="mt-3 rounded-lg bg-cyan-600/80 px-4 py-1.5 text-xs font-medium text-white hover:bg-cyan-500 transition"
                            >
                                Reset Filters
                            </button>
                        </div>
                    )}
                </section>

                {/* ── Footer ── */}
                <footer className="mt-16 border-t border-slate-800 pt-6 text-center text-xs text-slate-600">
                    Smart Air Quality Assistant &middot; Data: <span className="text-slate-500">OpenAQ</span> &middot; Region: <span className="text-slate-500">India</span>
                </footer>
            </div>
        </div>
    );
}
