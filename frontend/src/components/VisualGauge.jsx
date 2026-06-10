import React from 'react';

export default function VisualGauge({ probability, isVerified }) {
  // If verified, force 0% fake probability
  const displayProbability = isVerified ? 0.0 : probability;
  const percentage = Math.round(displayProbability * 100);
  
  const radius = 55;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayProbability * circumference);
  
  let colorVar = 'var(--status-real)';
  let label = 'Real Account';
  let detailText = 'Low probability of being a bot.';

  if (isVerified) {
    colorVar = 'var(--status-real)';
    label = 'Verified Real';
    detailText = 'Bypassed AI scanner due to blue tick.';
  } else if (displayProbability > 0.8) {
    colorVar = 'var(--status-fake)';
    label = 'Highly Suspicious (Fake)';
    detailText = 'Very high probability of being an automated bot.';
  } else if (displayProbability > 0.5) {
    colorVar = 'var(--status-warn)';
    label = 'Suspicious (Likely Fake)';
    detailText = 'Moderate to high risk. Tread with caution.';
  } else if (displayProbability > 0.3) {
    colorVar = 'var(--status-warn)';
    label = 'Slightly Suspicious';
    detailText = 'Minor bot-like patterns detected.';
  }

  return (
    <div className="gauge-card text-center">
      <div className="gauge-container">
        <svg width="150" height="150" className="gauge-svg">
          {/* Background Circle */}
          <circle
            cx="75"
            cy="75"
            r={radius}
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Foreground Colored Circle */}
          <circle
            cx="75"
            cy="75"
            r={radius}
            stroke={colorVar}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 0.8s ease-in-out',
              transform: 'rotate(-90deg)',
              transformOrigin: '50% 50%'
            }}
          />
        </svg>
        <div className="gauge-text-overlay">
          <span className="gauge-percentage">{percentage}%</span>
          <span className="gauge-sub">Fake Risk</span>
        </div>
      </div>
      
      <div className="gauge-info mt-4">
        <h3 className="gauge-label" style={{ color: colorVar }}>{label}</h3>
        <p className="gauge-description">{detailText}</p>
      </div>
    </div>
  );
}
