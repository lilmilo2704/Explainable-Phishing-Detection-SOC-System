const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

const GlobalFeatureImportance3DVector = ({ features = [] }) => {
  const width = 980;
  const rowHeight = 36;
  const topPad = 28;
  const bottomPad = 24;
  const leftLabel = 220;
  const graphWidth = 660;
  const depthX = 10;
  const depthY = 7;
  const maxVal = Math.max(...features.map((f) => Number(f.importance || 0)), 0.0001);
  const totalHeight = topPad + bottomPad + Math.max(features.length, 1) * rowHeight;

  return (
    <svg
      viewBox={`0 0 ${width} ${totalHeight}`}
      style={{ width: '100%', height: 'auto', display: 'block' }}
      role="img"
      aria-label="3D vector graph of global feature importance"
    >
      <defs>
        <linearGradient id="barFront" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#0f7bd8" />
          <stop offset="100%" stopColor="#39b0ff" />
        </linearGradient>
        <linearGradient id="barTop" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#84d4ff" />
          <stop offset="100%" stopColor="#2d93de" />
        </linearGradient>
        <linearGradient id="barSide" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1770bf" />
          <stop offset="100%" stopColor="#0d4e8e" />
        </linearGradient>
      </defs>

      <line x1={leftLabel} y1={topPad - 10} x2={leftLabel + graphWidth} y2={topPad - 10} stroke="rgba(255,255,255,0.16)" />

      {features.map((feat, i) => {
        const y = topPad + i * rowHeight;
        const raw = Number(feat.importance || 0);
        const norm = clamp(raw / maxVal, 0, 1);
        const barW = Math.max(8, norm * graphWidth);
        const x0 = leftLabel;
        const y0 = y;
        const h = 18;

        const front = `${x0},${y0} ${x0 + barW},${y0} ${x0 + barW},${y0 + h} ${x0},${y0 + h}`;
        const top = `${x0},${y0} ${x0 + depthX},${y0 - depthY} ${x0 + barW + depthX},${y0 - depthY} ${x0 + barW},${y0}`;
        const side = `${x0 + barW},${y0} ${x0 + barW + depthX},${y0 - depthY} ${x0 + barW + depthX},${y0 + h - depthY} ${x0 + barW},${y0 + h}`;

        return (
          <g key={`${feat.feature}-${i}`}>
            <text x={8} y={y0 + 13} fill="var(--text-primary)" fontSize="12" fontWeight="600">
              {feat.feature}
            </text>
            <text x={8} y={y0 + 27} fill="var(--text-secondary)" fontSize="10">
              {raw.toFixed(3)}
            </text>

            <rect
              x={leftLabel}
              y={y0}
              width={graphWidth}
              height={h}
              fill="rgba(255,255,255,0.04)"
              rx="2"
            />
            <polygon points={front} fill="url(#barFront)" />
            <polygon points={top} fill="url(#barTop)" />
            <polygon points={side} fill="url(#barSide)" />
          </g>
        );
      })}
    </svg>
  );
};

export default GlobalFeatureImportance3DVector;
