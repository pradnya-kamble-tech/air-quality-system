/**
 * AqiLegend — horizontal color-coded AQI category legend.
 */

const AQI_BANDS = [
    { label: "Good", range: "0–50", color: "#34d399" },
    { label: "Moderate", range: "51–100", color: "#fbbf24" },
    { label: "Unhealthy (Sensitive)", range: "101–150", color: "#fb923c" },
    { label: "Unhealthy", range: "151–200", color: "#f87171" },
    { label: "Very Unhealthy", range: "201–300", color: "#a78bfa" },
    { label: "Hazardous", range: "301–500", color: "#9f1239" },
];

export default function AqiLegend() {
    return (
        <section id="aqi-legend" className="dashboard-section">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                🎨 AQI Scale
            </h2>
            <div className="flex flex-wrap gap-2">
                {AQI_BANDS.map((band) => (
                    <div
                        key={band.label}
                        className="flex items-center gap-2 rounded-lg bg-slate-800/60 border border-slate-700/40 px-3 py-2 text-xs transition hover:bg-slate-800"
                    >
                        <span
                            className="inline-block h-3 w-3 rounded-full shrink-0"
                            style={{ backgroundColor: band.color }}
                        />
                        <span className="font-medium text-slate-300">{band.label}</span>
                        <span className="text-slate-500">{band.range}</span>
                    </div>
                ))}
            </div>
        </section>
    );
}
