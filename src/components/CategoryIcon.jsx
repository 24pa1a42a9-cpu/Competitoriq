import React from 'react';

export default function CategoryIcon({ category, size = 18, style = {} }) {
  const norm = (category || '').toLowerCase();

  if (norm.includes('product')) {
    // Package / Product Launch Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="#fdf2f4" />
        <path d="M2 17L12 22L22 17" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M2 12L12 17L22 12" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="12" cy="7" r="1.5" fill="#ea96a5" />
      </svg>
    );
  }

  if (norm.includes('pricing')) {
    // Price Tag / Currency Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <path d="M20.59 13.41L13.42 20.58C13.0483 20.9529 12.5437 21.1625 12.0175 21.1625C11.4913 21.1625 10.9867 20.9529 10.615 20.58L3 13V3H13L20.59 10.59C20.9625 10.9621 21.1718 11.4669 21.1718 11.993C21.1718 12.5191 20.9625 13.0239 20.59 13.396V13.41Z" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="#fdf2f4" />
        <circle cx="7.5" cy="7.5" r="1.5" fill="#0a0a0a" />
        <path d="M12 11V15M14 12H10" stroke="#0a0a0a" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    );
  }

  if (norm.includes('hiring') || norm.includes('talent')) {
    // People / Talent Migration Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <path d="M16 21V19C16 17.9391 15.5786 16.9217 14.8284 16.1716C14.0783 15.4214 13.0609 15 12 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="8.5" cy="7" r="4" stroke="#0a0a0a" strokeWidth="2" fill="#fdf2f4" />
        <path d="M20 8V14M23 11H17" stroke="#ea96a5" strokeWidth="2" strokeLinecap="round" />
      </svg>
    );
  }

  if (norm.includes('messaging') || norm.includes('speech')) {
    // Speech Bubble / Narrative Shift Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0034 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z" stroke="#0a0a0a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="#fdf2f4" />
        <circle cx="9" cy="11.5" r="1" fill="#0a0a0a" />
        <circle cx="13" cy="11.5" r="1" fill="#0a0a0a" />
        <circle cx="17" cy="11.5" r="1" fill="#ea96a5" />
      </svg>
    );
  }

  if (norm.includes('partnership') || norm.includes('deal')) {
    // Handshake / Partnership Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <path d="M18 10L14 6L10 10L14 14L18 10Z" stroke="#0a0a0a" strokeWidth="2" fill="#fdf2f4" />
        <path d="M6 14L2 10L6 6L10 10L6 14Z" stroke="#0a0a0a" strokeWidth="2" />
        <path d="M14 14L18 18H22V14L18 10" stroke="#0a0a0a" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M10 14L6 18H2V14L6 10" stroke="#0a0a0a" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="14" cy="10" r="1" fill="#ea96a5" />
      </svg>
    );
  }

  if (norm.includes('strategy') || norm.includes('pattern') || norm.includes('announcement')) {
    // Compass / Target Strategic Direction Illustration
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
        <circle cx="12" cy="12" r="10" stroke="#0a0a0a" strokeWidth="2" fill="#fdf2f4" />
        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" stroke="#0a0a0a" strokeWidth="1.8" fill="#0a0a0a" />
        <circle cx="12" cy="12" r="2" fill="#ea96a5" />
      </svg>
    );
  }

  // Fallback: Node Memory Icon
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, ...style }}>
      <circle cx="12" cy="12" r="9" stroke="#0a0a0a" strokeWidth="2" fill="#fdf2f4" />
      <circle cx="12" cy="12" r="4" fill="#0a0a0a" />
      <circle cx="12" cy="12" r="1.5" fill="#ea96a5" />
    </svg>
  );
}
