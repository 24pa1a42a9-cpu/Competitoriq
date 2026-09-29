import React from 'react';
import {
  Compass,
  Building2,
  History,
  GitMerge,
  TrendingUp,
  Database,
  Sparkles,
  Columns,
  Bell,
  Scale,
  FileText,
  Settings,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import AgentMascot from './AgentMascot';

export default function Sidebar({ currentView, onSelectView, alertsCount = 2, onOpenSettings }) {
  const navItems = [
    { id: 'overview', label: 'Intelligence Overview', icon: Compass },
    { id: 'competitors', label: 'Competitors', icon: Building2 },
    { id: 'timeline', label: 'Activity Timeline', icon: History },
    { id: 'dots', label: 'Connect the Dots', icon: GitMerge },
    { id: 'patterns', label: 'Strategic Patterns', icon: TrendingUp },
    { id: 'memory', label: 'Hindsight Memory', icon: Database },
    { id: 'analyst', label: 'AI Analyst', icon: Sparkles },
    { id: 'before-after', label: 'Before vs After', icon: Columns },
    { id: 'alerts', label: 'Alerts', icon: Bell, badge: alertsCount },
    { id: 'comparison', label: 'Competitive Comparison', icon: Scale },
    { id: 'report', label: 'Executive Report', icon: FileText }
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header with CompetitorIQ Mascot */}
      <div style={{ padding: '18px 18px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AgentMascot size={36} state="watching" />
          <div>
            <div style={{ fontWeight: 800, fontSize: '15px', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              CompetitorIQ
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 500 }}>
              AI Intelligence Agent
            </div>
          </div>
        </div>

        {/* Core Story Micro-Banner */}
        <div style={{
          marginTop: '12px',
          padding: '6px 8px',
          backgroundColor: 'var(--pink-lightest)',
          border: '1px solid var(--pink-border)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '9.5px',
          fontFamily: 'var(--font-mono)',
          fontWeight: 700,
          color: 'var(--text-primary)',
          letterSpacing: '0.02em',
          textAlign: 'center'
        }}>
          EVENT → MEMORY → PATTERN → INSIGHT
        </div>
      </div>

      {/* Navigation List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 10px' }}>
        <div style={{
          fontSize: '10px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--text-muted)',
          padding: '6px 10px 4px'
        }}>
          Intelligence Engine
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-md)',
                  border: isActive ? '1px solid var(--pink-border)' : '1px solid transparent',
                  backgroundColor: isActive ? 'var(--pink-subtle)' : 'transparent',
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.12s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                    e.currentTarget.style.color = 'var(--text-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = 'var(--text-secondary)';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Icon size={16} strokeWidth={isActive ? 2.3 : 1.8} color="currentColor" />
                  <span>{item.label}</span>
                </div>
                {item.badge && item.badge > 0 ? (
                  <span style={{
                    backgroundColor: 'var(--text-primary)',
                    color: 'var(--text-inverse)',
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '1px 6px',
                    borderRadius: 'var(--radius-full)'
                  }}>
                    {item.badge}
                  </span>
                ) : (
                  isActive && <ChevronRight size={14} strokeWidth={2.5} color="var(--text-primary)" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status & User Section */}
      <div style={{
        padding: '14px 16px',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-secondary)'
      }}>
        {/* Agent Activity Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '12px',
          fontSize: '11px',
          color: 'var(--text-secondary)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: 'var(--text-primary)',
              boxShadow: '0 0 0 2px var(--pink-surface)'
            }} />
            <span style={{ fontWeight: 600 }}>IQ-Agent: Monitoring</span>
          </div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)' }}>
            142 Memories
          </span>
        </div>

        {/* User Profile Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: '6px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '26px',
              height: '26px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--pink-surface)',
              border: '1px solid var(--border-medium)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-primary)'
            }}>
              <ShieldCheck size={14} />
            </div>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.1 }}>
                Intelligence Workspace
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                System Active • Hindsight Connected
              </div>
            </div>
          </div>

          <button
            onClick={onOpenSettings}
            title="Settings & API Configuration"
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              padding: '4px',
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <Settings size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}
