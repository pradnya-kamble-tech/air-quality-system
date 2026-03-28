/**
 * ScoreGauge — circular SVG gauge showing AQI score out of 10.
 */

const SCORE_COLORS = [
    { max: 3, color: "#f87171" },
    { max: 5, color: "#fb923c" },
    { max: 7, color: "#fbbf24" },
    { max: 9, color: "#34d399" },
    { max: 10, color: "#22d3ee" },
];

function getScoreColor(score) {
    for (const { max, color } of SCORE_COLORS) {
        if (score <= max) return color;
    }
    return "#22d3ee";
}

export default function ScoreGauge({ score, size = 64 }) {
    const radius = (size - 8) / 2;
    const circumference = 2 * Math.PI * radius;
    const progress = (score / 10) * circumference;
    const offset = circumference - progress;
    const color = getScoreColor(score);

    return (
        <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
            <svg width={size} height={size} className="-rotate-90">
                {/* Background ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="4"
                />
                {/* Progress ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="gauge-ring"
                    style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-sm font-black tabular-nums animate-count" style={{ color }}>
                    {score.toFixed(1)}
                </span>
                <span className="text-[8px] text-slate-500 -mt-0.5">/10</span>
            </div>
        </div>
    );
}
