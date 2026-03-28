/**
 * FilterBar — city and pollutant dropdown filters.
 */

export default function FilterBar({
    cities,
    pollutants,
    selectedCity,
    selectedPollutant,
    onCityChange,
    onPollutantChange,
}) {
    return (
        <section id="filters-section" className="dashboard-section">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                🔍 Filters
            </h2>
            <div className="flex flex-wrap items-center gap-3">
                {/* City filter */}
                <div className="flex items-center gap-2">
                    <label htmlFor="city-filter" className="text-xs text-slate-400">
                        City
                    </label>
                    <select
                        id="city-filter"
                        value={selectedCity}
                        onChange={(e) => onCityChange(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Cities</option>
                        {cities.map((city) => (
                            <option key={city} value={city}>
                                {city}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Pollutant filter */}
                <div className="flex items-center gap-2">
                    <label htmlFor="pollutant-filter" className="text-xs text-slate-400">
                        Pollutant
                    </label>
                    <select
                        id="pollutant-filter"
                        value={selectedPollutant}
                        onChange={(e) => onPollutantChange(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Pollutants</option>
                        {pollutants.map((p) => (
                            <option key={p} value={p}>
                                {p.toUpperCase()}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Reset button */}
                {(selectedCity !== "all" || selectedPollutant !== "all") && (
                    <button
                        onClick={() => {
                            onCityChange("all");
                            onPollutantChange("all");
                        }}
                        className="rounded-lg bg-slate-700/60 border border-slate-600/40 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-600/60 hover:text-white active:scale-95"
                    >
                        ✕ Reset
                    </button>
                )}
            </div>
        </section>
    );
}
