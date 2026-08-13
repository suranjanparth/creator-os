type TrendChartProps = { data: number[]; label?: string };

export function TrendChart({ data, label = "Performance trend" }: TrendChartProps) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 88 - ((value - min) / (max - min)) * 68;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="trend-chart" role="img" aria-label={label}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient id="chart-fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#9ff4c9" stopOpacity=".34" />
            <stop offset="100%" stopColor="#9ff4c9" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={`M 0,100 L ${points} L 100,100 Z`} fill="url(#chart-fill)" />
        <polyline points={points} fill="none" stroke="#9ff4c9" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      </svg>
    </div>
  );
}
