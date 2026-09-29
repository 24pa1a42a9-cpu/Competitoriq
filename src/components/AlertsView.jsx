import React, { useState, useEffect, useMemo } from 'react';
import {
  Bell,
  ShieldAlert,
  CheckCircle,
  Eye,
  ArrowRight,
  Filter,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  Check,
  XCircle,
  Clock,
  Sparkles,
  Database,
  History,
  Layers,
  Info
} from 'lucide-react';
import AgentMascot from './AgentMascot';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';
import competitorApi from '../services/api';

export default function AlertsView({ onSelectEvent, onSelectCompetitor }) {
  const [alerts, setAlerts] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedCompetitor, setSelectedCompetitor] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('active'); // 'active' (new+read), 'all', 'new', 'read', 'dismissed'
  const [loading, setLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState(null);
  const [checkpointData, setCheckpointData] = useState({
    lastChecked: null,
    newCount: 0,
    byCategory: {}
  });

  // Dynamic mascot states
  const [mascotState, setMascotState] = useState('watching');
  const [mascotSpeech, setMascotSpeech] = useState(
    'Watching competitors across verified corporate feeds and persistent memory banks...'
  );

  // Load initial data
  const loadData = async () => {
    try {
      setLoading(true);
      const [compsData, alertsData, eventsData] = await Promise.all([
        competitorApi.getCompetitors().catch(() => []),
        competitorApi.getAlerts().catch(() => []),
        competitorApi.getEvents().catch(() => [])
      ]);

      setCompetitors(compsData);
      setAlerts(alertsData);
      setEvents(eventsData);

      // Checkpoint info for selected or primary competitor
      const compId = selectedCompetitor !== 'all' ? selectedCompetitor : (compsData[0]?.id || 'microsoft');
      try {
        const changes = await competitorApi.getChanges(compId);
        setCheckpointData({
          lastChecked: changes.last_checkpoint || (alertsData[0]?.detectedAt ? alertsData[0].detectedAt : 'Active session baseline'),
          newCount: changes.event_count || 0,
          byCategory: changes.by_category || {}
        });
      } catch (err) {
        console.error('Error fetching changes checkpoint:', err);
      }

      // Configure initial mascot message
      const unreadCount = alertsData.filter(a => a.status === 'new').length;
      if (unreadCount > 0) {
        setMascotState('alert');
        setMascotSpeech(`I noticed ${unreadCount} new high-priority competitor development${unreadCount > 1 ? 's' : ''} connected to historical memory.`);
      } else {
        setMascotState('watching');
        setMascotSpeech('Watching competitors... All telemetry is up to date with Hindsight persistent memory.');
      }
    } catch (err) {
      console.error('Failed to load alerts view data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Update checkpoint whenever competitor selection changes
  useEffect(() => {
    const updateCheckpoint = async () => {
      const compId = selectedCompetitor !== 'all' ? selectedCompetitor : (competitors[0]?.id || 'microsoft');
      try {
        const changes = await competitorApi.getChanges(compId);
        setCheckpointData({
          lastChecked: changes.last_checkpoint || 'Active session baseline',
          newCount: changes.event_count || 0,
          byCategory: changes.by_category || {}
        });
      } catch (err) {
        // Fallback gracefully
      }
    };
    if (competitors.length > 0) {
      updateCheckpoint();
    }
  }, [selectedCompetitor, competitors]);

  // Run Proactive Scan / Generate Alerts
  const handleRunScan = async () => {
    setIsScanning(true);
    setScanMessage(null);
    setMascotState('thinking');
    setMascotSpeech('Comparing new competitor activity with previous checkpoint and recalling historical Hindsight memory...');

    const targetCompetitor = selectedCompetitor !== 'all'
      ? (competitors.find(c => c.id === selectedCompetitor)?.name || selectedCompetitor)
      : 'Microsoft';

    try {
      const res = await competitorApi.generateAlerts(targetCompetitor);
      
      // Refresh alerts list & checkpoint
      const updatedAlerts = await competitorApi.getAlerts();
      setAlerts(updatedAlerts);

      const targetCompId = selectedCompetitor !== 'all' ? selectedCompetitor : 'microsoft';
      const updatedChanges = await competitorApi.getChanges(targetCompId).catch(() => ({}));
      setCheckpointData({
        lastChecked: res.checkpoint || updatedChanges.last_checkpoint || new Date().toISOString().replace('T', ' ').substring(0, 19),
        newCount: updatedChanges.event_count || 0,
        byCategory: updatedChanges.by_category || {}
      });

      if (res.alerts_generated > 0) {
        setMascotState('alert');
        setMascotSpeech(`I identified ${res.alerts_generated} significant strategic alert${res.alerts_generated > 1 ? 's' : ''} for ${res.competitor} grounded in Hindsight history.`);
        setScanMessage({
          type: 'success',
          text: `Scan complete: Synthesized ${res.alerts_generated} evidence-grounded alert(s) for ${res.competitor}.`
        });
      } else {
        setMascotState('watching');
        setMascotSpeech('No significant new competitor activity since your last check.');
        setScanMessage({
          type: 'info',
          text: res.message || 'No significant new competitor activity since your last check.'
        });
      }
    } catch (err) {
      console.error('Scan error:', err);
      setMascotState('watching');
      setMascotSpeech('Encountered an issue running proactive scan. Existing intelligence remains verified.');
      setScanMessage({
        type: 'error',
        text: 'Failed to complete proactive intelligence scan.'
      });
    } finally {
      setIsScanning(false);
    }
  };

  // Mark Alert Read
  const handleMarkRead = async (alertId) => {
    try {
      await competitorApi.markAlertRead(alertId);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: 'read' } : a));
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  };

  // Dismiss Alert
  const handleDismiss = async (alertId) => {
    try {
      await competitorApi.dismissAlert(alertId);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: 'dismissed' } : a));
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  // Filter Alerts
  const filteredAlerts = useMemo(() => {
    return alerts.filter(a => {
      // Competitor filter
      if (selectedCompetitor !== 'all' && (a.competitorId || '').toLowerCase() !== selectedCompetitor.toLowerCase()) {
        return false;
      }
      // Severity filter
      if (selectedSeverity !== 'all') {
        const sevNorm = (a.severity || '').toLowerCase();
        if (selectedSeverity === 'critical' && !sevNorm.includes('high') && !sevNorm.includes('critical')) return false;
        if (selectedSeverity === 'high' && !sevNorm.includes('high')) return false;
        if (selectedSeverity === 'medium' && !sevNorm.includes('medium')) return false;
        if (selectedSeverity === 'informational' && !sevNorm.includes('info')) return false;
      }
      // Status filter
      if (selectedStatus === 'active') {
        if (a.status === 'dismissed') return false;
      } else if (selectedStatus !== 'all') {
        if (a.status !== selectedStatus) return false;
      }
      return true;
    });
  }, [alerts, selectedCompetitor, selectedSeverity, selectedStatus]);

  const activeAlertsCount = alerts.filter(a => a.status === 'new').length;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* View Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-black" style={{ fontSize: '10.5px' }}>STEP 11</span>
            <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Proactive Intelligence Engine
            </span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', margin: 0 }}>
            What Changed? & Strategic Alerts
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '6px', maxWidth: '780px' }}>
            Autonomous change detection comparing your previous checkpoint with newly ingested telemetry.
            Hindsight recalls episodic competitor history so Groq analyzes whether changes signal a meaningful strategic shift.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="cautious-pill">
            <ShieldAlert size={12} color="var(--text-primary)" />
            <span>GROUNDED IN REAL TELEMETRY</span>
          </div>
          <button
            onClick={handleRunScan}
            disabled={isScanning}
            className="btn btn-primary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '12.5px', padding: '8px 16px' }}
          >
            <RefreshCw size={13} className={isScanning ? 'animate-spin' : ''} />
            <span>{isScanning ? 'Scanning Memory Banks...' : 'Check for New Changes'}</span>
          </button>
        </div>
      </div>

      {/* Mascot Proactive State & Explanation Callout */}
      <div style={{
        padding: '16px 22px',
        backgroundColor: mascotState === 'alert' ? 'var(--pink-lightest)' : 'var(--bg-secondary)',
        border: mascotState === 'alert' ? '1.5px solid var(--border-black)' : '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        transition: 'all 0.2s ease'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <AgentMascot size={42} state={mascotState} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>
                IQ-Agent Proactive Monitor
              </span>
              <span className={`badge ${mascotState === 'alert' ? 'badge-pink' : 'badge-outline'}`} style={{ fontSize: '10px' }}>
                {mascotState === 'thinking' ? 'Analyzing' : mascotState === 'alert' ? 'New Change Detected' : 'Watching Competitors'}
              </span>
            </div>
            <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '2px', lineHeight: 1.45 }}>
              {mascotSpeech}
            </div>
          </div>
        </div>

        {activeAlertsCount > 0 && (
          <span className="badge badge-black" style={{ flexShrink: 0, padding: '4px 10px' }}>
            {activeAlertsCount} Unread Alert{activeAlertsCount > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Scan Feedback Notification */}
      {scanMessage && (
        <div style={{
          padding: '12px 18px',
          borderRadius: 'var(--radius-sm)',
          fontSize: '12.5px',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: scanMessage.type === 'success' ? 'var(--pink-subtle)' : scanMessage.type === 'error' ? '#fdf2f2' : 'var(--bg-secondary)',
          border: `1px solid ${scanMessage.type === 'success' ? 'var(--pink-border)' : scanMessage.type === 'error' ? '#f8b4b4' : 'var(--border-subtle)'}`,
          color: 'var(--text-primary)'
        }}>
          {scanMessage.type === 'success' ? <CheckCircle size={15} color="#0a0a0a" /> : <Info size={15} color="var(--text-secondary)" />}
          <span>{scanMessage.text}</span>
        </div>
      )}

      {/* "SINCE I LAST CHECKED" Status Panel */}
      <div className="card" style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-primary)',
        borderColor: 'var(--border-subtle)',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--pink-lightest)',
            border: '1px solid var(--pink-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Clock size={16} color="var(--text-primary)" />
          </div>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Last Checked Checkpoint
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '2px' }}>
              {checkpointData.lastChecked || 'Baseline Active'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Database size={16} color="var(--text-primary)" />
          </div>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              New Activity Since Checkpoint
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {checkpointData.newCount} verified events
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: activeAlertsCount > 0 ? 'var(--pink-subtle)' : 'var(--bg-secondary)',
            border: `1px solid ${activeAlertsCount > 0 ? 'var(--pink-border)' : 'var(--border-subtle)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Bell size={16} color="var(--text-primary)" />
          </div>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Strategic Alert Signals
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: activeAlertsCount > 0 ? '#b8324f' : 'var(--text-primary)', marginTop: '2px' }}>
              {activeAlertsCount} unread ({alerts.length} total)
            </div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '14px',
        padding: '12px 18px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)'
      }}>
        {/* Competitor Filter Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginRight: '4px' }}>
            Competitor:
          </span>
          <button
            onClick={() => setSelectedCompetitor('all')}
            style={{
              padding: '4px 10px',
              fontSize: '11.5px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: selectedCompetitor === 'all' ? '1px solid var(--border-black)' : '1px solid var(--border-subtle)',
              backgroundColor: selectedCompetitor === 'all' ? 'var(--text-primary)' : 'var(--bg-primary)',
              color: selectedCompetitor === 'all' ? '#ffffff' : 'var(--text-secondary)',
              cursor: 'pointer'
            }}
          >
            All Competitors
          </button>
          {competitors.map(c => (
            <button
              key={c.id}
              onClick={() => setSelectedCompetitor(c.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                fontSize: '11.5px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: selectedCompetitor === c.id ? '1px solid var(--border-black)' : '1px solid var(--border-subtle)',
                backgroundColor: selectedCompetitor === c.id ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <CompanyLogo competitorId={c.id} size={14} />
              <span>{c.name}</span>
            </button>
          ))}
        </div>

        {/* Status & Severity Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {/* Status Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Status:
            </span>
            {[
              { id: 'active', label: 'Active' },
              { id: 'new', label: 'Unread' },
              { id: 'read', label: 'Read' },
              { id: 'dismissed', label: 'Dismissed' },
              { id: 'all', label: 'All' }
            ].map(st => (
              <button
                key={st.id}
                onClick={() => setSelectedStatus(st.id)}
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  border: selectedStatus === st.id ? '1px solid var(--border-black)' : '1px solid var(--border-medium)',
                  backgroundColor: selectedStatus === st.id ? 'var(--bg-primary)' : 'transparent',
                  color: selectedStatus === st.id ? 'var(--text-primary)' : 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                {st.label}
              </button>
            ))}
          </div>

          {/* Severity Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Severity:
            </span>
            {['all', 'high', 'medium', 'informational'].map(sev => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  border: selectedSeverity === sev ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                  backgroundColor: selectedSeverity === sev ? 'var(--text-primary)' : 'var(--bg-primary)',
                  color: selectedSeverity === sev ? '#ffffff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* Alerts Feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {loading ? (
          <div className="card" style={{ padding: '60px', textAlign: 'center' }}>
            <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px', color: 'var(--text-muted)' }} />
            <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Loading proactive competitive alerts & historical memory context...
            </div>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="card" style={{ padding: '50px 30px', textAlign: 'center' }}>
            <CheckCircle size={32} color="#0a0a0a" style={{ margin: '0 auto 12px' }} />
            <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)' }}>
              No significant new competitor activity since your last check.
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '500px', margin: '6px auto 16px' }}>
              All observed telemetry has been evaluated against Hindsight persistent memories.
              Click "Check for New Changes" to scan for recently ingested events.
            </p>
            <button
              onClick={handleRunScan}
              disabled={isScanning}
              className="btn btn-outline btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', margin: '0 auto' }}
            >
              <RefreshCw size={12} className={isScanning ? 'animate-spin' : ''} />
              <span>Run Intelligence Scan</span>
            </button>
          </div>
        ) : (
          filteredAlerts.map(alt => {
            const isUnread = alt.status === 'new';
            const isDismissed = alt.status === 'dismissed';
            const matchedEvent = events.find(e => e.id === alt.eventId);

            return (
              <div
                key={alt.id}
                className="card"
                style={{
                  padding: '22px 26px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                  backgroundColor: isUnread ? 'var(--pink-lightest)' : isDismissed ? 'var(--bg-secondary)' : 'var(--bg-primary)',
                  borderColor: isUnread ? 'var(--border-black)' : 'var(--border-subtle)',
                  borderLeft: isUnread ? '5px solid var(--border-black)' : isDismissed ? '3px solid var(--border-medium)' : '1px solid var(--border-subtle)',
                  opacity: isDismissed ? 0.75 : 1,
                  transition: 'background-color 0.15s ease'
                }}
              >
                {/* Meta Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <CompanyLogo competitorId={alt.competitorId} size={22} />
                    <span style={{ fontWeight: 800, fontSize: '14px', color: 'var(--text-primary)' }}>
                      {alt.competitorName}
                    </span>
                    
                    {/* Severity Pill */}
                    <span className={
                      alt.severity?.toLowerCase().includes('high')
                        ? 'badge badge-black'
                        : alt.severity?.toLowerCase().includes('medium')
                          ? 'badge badge-pink'
                          : 'badge badge-outline'
                    }>
                      {alt.severity || 'Medium attention'}
                    </span>

                    {/* Status Pill */}
                    {isUnread && (
                      <span className="badge badge-black" style={{ backgroundColor: '#0a0a0a', color: '#fcebee' }}>
                        NEW SIGNAL
                      </span>
                    )}
                    {alt.status === 'read' && (
                      <span className="badge badge-outline" style={{ fontSize: '10.5px' }}>
                        ACKNOWLEDGED
                      </span>
                    )}
                    {isDismissed && (
                      <span className="badge badge-outline" style={{ fontSize: '10.5px', color: 'var(--text-muted)' }}>
                        DISMISSED
                      </span>
                    )}

                    {/* Category Pill */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                      <CategoryIcon category={alt.eventType} size={14} />
                      <span style={{ fontWeight: 600 }}>{alt.eventType}</span>
                    </div>
                  </div>

                  {/* Actions & Timestamp */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {alt.detectedAt || 'Recently observed'}
                    </span>

                    {isUnread ? (
                      <button
                        onClick={() => handleMarkRead(alt.id)}
                        className="btn btn-outline btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px', padding: '3px 8px' }}
                        title="Mark alert as read"
                      >
                        <Check size={12} />
                        <span>Mark Read</span>
                      </button>
                    ) : alt.status === 'read' ? (
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        <CheckCircle size={12} /> Read
                      </span>
                    ) : null}

                    {!isDismissed ? (
                      <button
                        onClick={() => handleDismiss(alt.id)}
                        className="btn btn-ghost btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px', padding: '3px 6px', color: 'var(--text-muted)' }}
                        title="Dismiss alert (preserves underlying evidence)"
                      >
                        <XCircle size={12} />
                        <span>Dismiss</span>
                      </button>
                    ) : null}
                  </div>
                </div>

                {/* Section 1: WHAT CHANGED? */}
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em', marginBottom: '4px' }}>
                    What Changed?
                  </div>
                  <h3 style={{ fontSize: '16.5px', fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 6px 0', letterSpacing: '-0.01em' }}>
                    {alt.title}
                  </h3>
                  <p style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.55, margin: 0 }}>
                    {alt.whatChanged}
                  </p>
                </div>

                {/* Section 2: WHY IT MATTERS */}
                <div style={{
                  padding: '12px 16px',
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em', marginBottom: '4px' }}>
                    Why It Matters
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                    {alt.whyItMatters}
                  </p>
                </div>

                {/* Section 3: HISTORICAL CONTEXT & HINDSIGHT MEMORY */}
                {alt.historicalContext && (
                  <div className="intel-quote" style={{ fontSize: '12.5px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                      <History size={13} color="var(--text-primary)" />
                      <span style={{ fontWeight: 800, textTransform: 'uppercase', fontSize: '10.5px', letterSpacing: '0.04em' }}>
                        Historical Context & Hindsight Memory Connection
                      </span>
                    </div>
                    <p style={{ margin: '0 0 8px 0', lineHeight: 1.5, color: 'var(--text-primary)' }}>
                      {alt.historicalContext}
                    </p>

                    {/* Supporting Timeline Events */}
                    {alt.supportingEvents && alt.supportingEvents.length > 0 && (
                      <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed var(--pink-border)' }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                          Related Historical Moves:
                        </span>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {alt.supportingEvents.map((se, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11.5px' }}>
                              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', flexShrink: 0 }}>
                                [{se.date || 'Past'}]
                              </span>
                              <span className="badge badge-outline" style={{ fontSize: '9.5px', padding: '1px 5px' }}>
                                {se.eventType || 'Event'}
                              </span>
                              <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>
                                {se.title}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Section 4: EVIDENCE & SOURCE TRANSPARENCY */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '8px',
                  borderTop: '1px solid var(--border-subtle)',
                  flexWrap: 'wrap',
                  gap: '12px'
                }}>
                  {/* Memory Used Transparency Badge */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                      backgroundColor: 'var(--bg-secondary)',
                      padding: '3px 8px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-subtle)'
                    }}>
                      <Database size={11} />
                      <span>
                        Memory Grounding: {alt.memoryUsed?.count || 0} nodes
                        {alt.memoryUsed?.earliest ? ` (${alt.memoryUsed.earliest} → ${alt.memoryUsed.latest})` : ''}
                      </span>
                    </div>

                    <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      ID: {alt.id}
                    </span>
                  </div>

                  {/* Verified Source Link & Inspect Evidence */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {alt.sourceUrl ? (
                      <a
                        href={alt.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-outline btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', textDecoration: 'none' }}
                      >
                        <ExternalLink size={12} />
                        <span>Source: {alt.sourceName || 'Official Telemetry'}</span>
                      </a>
                    ) : (
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        Source: {alt.sourceName || 'Verified Corporate Feed'}
                      </span>
                    )}

                    {matchedEvent && (
                      <button
                        onClick={() => onSelectEvent(matchedEvent)}
                        className="btn btn-ghost btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      >
                        <Eye size={12} />
                        <span>Inspect Raw Evidence</span>
                      </button>
                    )}
                  </div>
                </div>

              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
