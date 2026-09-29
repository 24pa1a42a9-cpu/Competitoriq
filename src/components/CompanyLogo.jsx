import React from 'react';

export default function CompanyLogo({ competitorId, size = 28, style = {} }) {
  const id = (competitorId || '').toLowerCase();

  if (id.includes('nova')) {
    // NovaAI: Stylized geometric supernova star / constellation
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <polygon points="12 2 15 9 22 12 15 15 12 22 9 15 2 12 9 9" fill="#ffffff" stroke="#ffffff" strokeWidth="1" />
          <circle cx="12" cy="12" r="2.5" fill="#fce7ea" />
        </svg>
      </div>
    );
  }

  if (id.includes('cloud')) {
    // CloudMind: Neural compute cloud with pink synaptic core
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#fcebee',
        border: '1.5px solid #0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M17.5 19H9C6.23858 19 4 16.7614 4 14C4 11.4586 5.89745 9.35977 8.35824 9.0494C9.0924 6.71534 11.2828 5 13.8889 5C17.0706 5 19.6738 7.50284 19.8242 10.6558C20.5284 11.1738 21 12.0305 21 13C21 14.6569 19.6569 16 18 16" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="13" cy="12" r="2" fill="#ea96a5" />
        </svg>
      </div>
    );
  }

  if (id.includes('tech') || id.includes('flow')) {
    // TechFlow: Orchestration flow infinity loop / pipeline
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 12C4 8.5 7.5 8.5 9.5 12C11.5 15.5 15 15.5 15 12C15 8.5 18.5 8.5 20.5 12" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" />
          <circle cx="9.5" cy="12" r="2" fill="#ea96a5" />
          <circle cx="15" cy="12" r="2" fill="#fce7ea" />
        </svg>
      </div>
    );
  }

  if (id.includes('microsoft') || id.includes('msft')) {
    // Microsoft: 4-square grid with brand aesthetic
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="2" width="9" height="9" fill="#f25022" rx="1" />
          <rect x="13" y="2" width="9" height="9" fill="#7fba00" rx="1" />
          <rect x="2" y="13" width="9" height="9" fill="#00a4ef" rx="1" />
          <rect x="13" y="13" width="9" height="9" fill="#ffb900" rx="1" />
        </svg>
      </div>
    );
  }

  if (id.includes('google') || id.includes('alphabet')) {
    // Google: Clean 'G' glyph
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#ffffff',
        border: '1.5px solid #0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21.35 11.1H12v3.8h5.38c-.46 2.2-2.3 3.8-5.38 3.8-3.3 0-6-2.7-6-6s2.7-6 6-6c1.45 0 2.8.55 3.82 1.45l2.85-2.85C16.97 3.05 14.65 2 12 2 6.48 2 2 6.48 2 12s4.48 10 10 10c5.77 0 9.6-4.06 9.6-9.77 0-.75-.07-1.3-.25-1.13z" fill="#0a0a0a" />
        </svg>
      </div>
    );
  }

  if (id.includes('openai')) {
    // OpenAI: Minimal spiral whorl
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" stroke="#fcebee" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2z" />
          <path d="m12 6 3 6-3 6-3-6 3-6z" />
          <circle cx="12" cy="12" r="2" fill="#ea96a5" />
        </svg>
      </div>
    );
  }

  if (id.includes('anthropic') || id.includes('claude')) {
    // Anthropic: Minimalist letterform / neural prism
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#fcebee',
        border: '1.5px solid #0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <span style={{ fontSize: size * 0.55, fontWeight: 900, color: '#0a0a0a', fontFamily: 'serif' }}>A</span>
      </div>
    );
  }

  if (id.includes('amazon') || id.includes('aws')) {
    // Amazon/AWS: Bold A with signature arc
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 17c5 3 10 3 14 0" stroke="#ff9900" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M12 4L6 14h12L12 4z" fill="#ffffff" />
        </svg>
      </div>
    );
  }

  if (id.includes('meta')) {
    // Meta: Infinity loop
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '6px',
        backgroundColor: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style
      }}>
        <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round">
          <path d="M6 15c-2.5 0-4-1.8-4-3.5S3.5 8 6 8c2.5 0 4 3 6 4 2-1 3.5-4 6-4 2.5 0 4 1.8 4 3.5S20.5 15 18 15c-2.5 0-4-3-6-4-2 1-3.5 4-6 4z" />
        </svg>
      </div>
    );
  }

  // Fallback
  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: '6px',
      backgroundColor: '#0a0a0a',
      color: '#ffffff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: size * 0.45,
      fontWeight: 800,
      flexShrink: 0,
      ...style
    }}>
      {competitorId ? competitorId.slice(0, 2).toUpperCase() : 'CI'}
    </div>
  );
}
