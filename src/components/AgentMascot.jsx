import React from 'react';

/**
 * CompetitorIQ Agent Mascot ("IQ-Bot")
 * An intelligent, friendly AI agent that watches, remembers, and connects competitor moves.
 * Rendered as pure scalable SVG with subtle micro-animations and expressive emotional states.
 * Colors: Pure Black (#0a0a0a), White (#ffffff), and Soft Baby Pink (#fcebee, #f9d8de, #ea96a5).
 */
export default function AgentMascot({
  state = 'watching', // 'watching' | 'thinking' | 'found' | 'explaining' | 'alert'
  size = 48,
  showBubble = false,
  bubbleText = '',
  bubblePlacement = 'right', // 'right' | 'top'
  className = '',
  style = {}
}) {
  const isThinking = state === 'thinking';
  const isFound = state === 'found';
  const isExplaining = state === 'explaining';
  const isAlert = state === 'alert';

  return (
    <div
      className={`agent-mascot-container ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '12px',
        position: 'relative',
        ...style
      }}
    >
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <svg
          width={size}
          height={size}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Subtle Radar Wave (Continuous Surveillance) */}
          <circle
            cx="50"
            cy="12"
            r="8"
            stroke="#ea96a5"
            strokeWidth="1.5"
            opacity="0.6"
            className="mascot-radar-pulse"
          />
          <circle
            cx="50"
            cy="12"
            r="14"
            stroke="#ea96a5"
            strokeWidth="1.2"
            opacity="0.3"
            className="mascot-radar-pulse-outer"
          />

          {/* Top Surveillance Antenna Stem */}
          <line x1="50" y1="14" x2="50" y2="28" stroke="#0a0a0a" strokeWidth="3" strokeLinecap="round" />
          {/* Antenna Beacon / Satellite Sphere */}
          <circle cx="50" cy="12" r="5" fill="#ea96a5" stroke="#0a0a0a" strokeWidth="2.5" />
          <circle cx="48" cy="10" r="1.5" fill="#ffffff" />

          {/* Left & Right Headphone / Memory Receptor Pods */}
          <rect x="12" y="44" width="8" height="20" rx="4" fill="#0a0a0a" />
          <rect x="14" y="48" width="4" height="12" rx="2" fill="#f9d8de" />

          <rect x="80" y="44" width="8" height="20" rx="4" fill="#0a0a0a" />
          <rect x="82" y="48" width="4" height="12" rx="2" fill="#f9d8de" />

          {/* Head / Monitor Body */}
          <rect
            x="18"
            y="28"
            width="64"
            height="52"
            rx="16"
            fill="#ffffff"
            stroke="#0a0a0a"
            strokeWidth="3.5"
          />

          {/* Face Screen Visor */}
          <rect
            x="24"
            y="34"
            width="52"
            height="40"
            rx="10"
            fill="#fdf5f6"
            stroke="#0a0a0a"
            strokeWidth="2"
          />

          {/* Small Memory Circuit Line on Forehead */}
          <path
            d="M34 38H45L48 41H66"
            stroke="#f4bdc6"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <circle cx="34" cy="38" r="1.5" fill="#ea96a5" />
          <circle cx="66" cy="41" r="1.5" fill="#ea96a5" />

          {/* EYES & EXPRESSION BASED ON STATE */}

          {/* 1. WATCHING / DEFAULT STATE: Attentive, intelligent friendly eyes */}
          {state === 'watching' && (
            <g className="mascot-eyes-watching">
              {/* Left Eye */}
              <circle cx="40" cy="54" r="5" fill="#0a0a0a" />
              <circle cx="38.5" cy="52.5" r="1.8" fill="#ffffff" />
              {/* Right Eye */}
              <circle cx="60" cy="54" r="5" fill="#0a0a0a" />
              <circle cx="58.5" cy="52.5" r="1.8" fill="#ffffff" />
              {/* Soft friendly smile */}
              <path d="M47 62Q50 65 53 62" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" />
            </g>
          )}

          {/* 2. THINKING STATE: Scanning vector memories, glancing up */}
          {isThinking && (
            <g className="mascot-eyes-thinking">
              {/* Scanning eyes looking up-right */}
              <ellipse cx="43" cy="50" rx="4.5" ry="5.5" fill="#0a0a0a" />
              <circle cx="41.5" cy="48" r="1.6" fill="#ffffff" />

              <ellipse cx="63" cy="50" rx="4.5" ry="5.5" fill="#0a0a0a" />
              <circle cx="61.5" cy="48" r="1.6" fill="#ffffff" />

              {/* Inquisitive cute mouth */}
              <circle cx="50" cy="63" r="2" fill="#0a0a0a" />

              {/* 3 scanning memory dots */}
              <circle cx="42" cy="65" r="1.2" fill="#ea96a5" />
              <circle cx="50" cy="67" r="1.2" fill="#ea96a5" />
              <circle cx="58" cy="65" r="1.2" fill="#ea96a5" />
            </g>
          )}

          {/* 3. FOUND / ALERT STATE: Sparkle in eyes, pattern discovered! */}
          {(isFound || isAlert) && (
            <g className="mascot-eyes-found">
              {/* Sparkle Left Eye */}
              <path
                d="M40 47L41.5 52L46.5 53.5L41.5 55L40 60L38.5 55L33.5 53.5L38.5 52L40 47Z"
                fill="#0a0a0a"
              />
              <circle cx="40" cy="53.5" r="1.5" fill="#ffffff" />

              {/* Sparkle Right Eye */}
              <path
                d="M60 47L61.5 52L66.5 53.5L61.5 55L60 60L58.5 55L53.5 53.5L58.5 52L60 47Z"
                fill="#0a0a0a"
              />
              <circle cx="60" cy="53.5" r="1.5" fill="#ffffff" />

              {/* Cheerful wide discovery smile */}
              <path
                d="M45 62Q50 67 55 62"
                stroke="#0a0a0a"
                strokeWidth="2.2"
                strokeLinecap="round"
                fill="#fcebee"
              />

              {/* Pink blush cheeks */}
              <circle cx="32" cy="58" r="2.5" fill="#f4bdc6" opacity="0.8" />
              <circle cx="68" cy="58" r="2.5" fill="#f4bdc6" opacity="0.8" />
            </g>
          )}

          {/* 4. EXPLAINING / INSIGHT STATE: Happy arched eyes, delivering insight */}
          {isExplaining && (
            <g className="mascot-eyes-explaining">
              {/* Happy curved eyes */}
              <path
                d="M35 55C35 51 44 51 44 55"
                stroke="#0a0a0a"
                strokeWidth="2.8"
                strokeLinecap="round"
              />
              <path
                d="M56 55C56 51 65 51 65 55"
                stroke="#0a0a0a"
                strokeWidth="2.8"
                strokeLinecap="round"
              />

              {/* Confident gentle smile */}
              <path
                d="M46 62C47.5 65 52.5 65 54 62"
                stroke="#0a0a0a"
                strokeWidth="2.2"
                strokeLinecap="round"
              />

              {/* Subtle pink cheeks */}
              <ellipse cx="32" cy="57" rx="3" ry="2" fill="#ea96a5" opacity="0.5" />
              <ellipse cx="68" cy="57" rx="3" ry="2" fill="#ea96a5" opacity="0.5" />
            </g>
          )}

          {/* Bottom Collar with "IQ" Memory Chip Emblem */}
          <path d="M42 80L50 85L58 80" stroke="#0a0a0a" strokeWidth="2.5" fill="#ffffff" />
          <rect x="44" y="81" width="12" height="6" rx="3" fill="#ea96a5" stroke="#0a0a0a" strokeWidth="1.5" />
        </svg>
      </div>

      {/* Optional Attached Speech Bubble */}
      {showBubble && bubbleText && (
        <div
          style={{
            position: 'relative',
            backgroundColor: '#ffffff',
            border: '1.5px solid #0a0a0a',
            borderRadius: '10px',
            padding: '8px 14px',
            fontSize: '12.5px',
            fontWeight: 600,
            color: '#0a0a0a',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            maxWidth: '380px',
            lineHeight: 1.45
          }}
        >
          {/* Bubble Pointer Arrow */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '-7px',
              transform: 'translateY(-50%) rotate(45deg)',
              width: '10px',
              height: '10px',
              backgroundColor: '#ffffff',
              borderLeft: '1.5px solid #0a0a0a',
              borderBottom: '1.5px solid #0a0a0a'
            }}
          />
          {bubbleText}
        </div>
      )}
    </div>
  );
}
