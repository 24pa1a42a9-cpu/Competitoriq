import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewView from './components/OverviewView';
import CompetitorsView from './components/CompetitorsView';
import CompetitorProfileModal from './components/CompetitorProfileModal';
import TimelineView from './components/TimelineView';
import ConnectDotsView from './components/ConnectDotsView';
import PatternsView from './components/PatternsView';
import HindsightMemoryView from './components/HindsightMemoryView';
import AiAnalystView from './components/AiAnalystView';
import BeforeAfterView from './components/BeforeAfterView';
import AlertsView from './components/AlertsView';
import ComparisonView from './components/ComparisonView';
import ExecutiveReportView from './components/ExecutiveReportView';
import EvidenceDrawer from './components/EvidenceDrawer';
import SettingsModal from './components/SettingsModal';
import { COMPETITORS, EVENTS } from './data/mockData';
import { competitorApi } from './services/api';

export default function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [selectedCompetitorId, setSelectedCompetitorId] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [analystQuery, setAnalystQuery] = useState('');
  const [competitors, setCompetitors] = useState([]);

  React.useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) setCompetitors(data);
      })
      .catch(err => console.warn('Could not load competitors in App:', err));
  }, []);

  const activeCompetitor = selectedCompetitorId
    ? (competitors.find(c => c.id === selectedCompetitorId || String(c.id).toLowerCase() === String(selectedCompetitorId).toLowerCase() || c.name.toLowerCase() === String(selectedCompetitorId).toLowerCase()) ||
       COMPETITORS.find(c => c.id === selectedCompetitorId) ||
       { id: selectedCompetitorId, name: selectedCompetitorId })
    : null;

  const handleOpenCompetitor = (competitorId) => {
    setSelectedCompetitorId(competitorId);
  };

  const handleOpenEvent = (event) => {
    setSelectedEvent(event);
  };

  const handleOpenMemoryFromDrawer = (memoryId) => {
    setSelectedEvent(null);
    setSelectedCompetitorId(null);
    setCurrentView('memory');
  };

  const handleOpenAnalystWithPrompt = (prompt) => {
    setAnalystQuery(prompt);
    setSelectedCompetitorId(null);
    setCurrentView('analyst');
  };

  return (
    <div className="app-container">
      {/* Left Navigation Sidebar */}
      <Sidebar
        currentView={currentView}
        onSelectView={(view) => {
          setCurrentView(view);
          window.scrollTo(0, 0);
        }}
        alertsCount={2}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Content Area */}
      <div className="main-content">
        {/* Top Header */}
        <Header
          currentView={currentView}
          onSelectView={(view) => setCurrentView(view)}
          onSelectCompetitor={(id) => handleOpenCompetitor(id)}
          onSelectEvent={(evt) => handleOpenEvent(evt)}
          alertsCount={2}
        />

        {/* View Router */}
        <main style={{ flex: 1 }}>
          {currentView === 'overview' && (
            <OverviewView
              onSelectView={(view) => setCurrentView(view)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectPattern={() => setCurrentView('patterns')}
            />
          )}

          {currentView === 'competitors' && (
            <CompetitorsView
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
              onSelectView={(view) => setCurrentView(view)}
            />
          )}

          {currentView === 'timeline' && (
            <TimelineView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
            />
          )}

          {currentView === 'dots' && (
            <ConnectDotsView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
              onSelectPattern={() => setCurrentView('patterns')}
            />
          )}

          {currentView === 'patterns' && (
            <PatternsView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
            />
          )}

          {currentView === 'memory' && (
            <HindsightMemoryView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
            />
          )}

          {currentView === 'analyst' && (
            <AiAnalystView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onOpenMemory={(memId) => {
                setCurrentView('memory');
              }}
              initialQuery={analystQuery}
            />
          )}

          {currentView === 'before-after' && (
            <BeforeAfterView />
          )}

          {currentView === 'alerts' && (
            <AlertsView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
            />
          )}

          {currentView === 'comparison' && (
            <ComparisonView
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
              onSelectView={(view) => setCurrentView(view)}
            />
          )}

          {currentView === 'report' && (
            <ExecutiveReportView
              onSelectEvent={(evt) => handleOpenEvent(evt)}
              onSelectCompetitor={(id) => handleOpenCompetitor(id)}
            />
          )}
        </main>
      </div>

      {/* Competitor Profile Modal */}
      {activeCompetitor && (
        <CompetitorProfileModal
          competitor={activeCompetitor}
          onClose={() => setSelectedCompetitorId(null)}
          onOpenEvent={(evt) => handleOpenEvent(evt)}
          onOpenAnalyst={(prompt) => handleOpenAnalystWithPrompt(prompt)}
        />
      )}

      {/* Evidence Drawer */}
      {selectedEvent && (
        <EvidenceDrawer
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onOpenCompetitor={(id) => {
            setSelectedEvent(null);
            handleOpenCompetitor(id);
          }}
          onOpenMemory={(memId) => handleOpenMemoryFromDrawer(memId)}
        />
      )}

      {/* Settings Modal */}
      {isSettingsOpen && (
        <SettingsModal onClose={() => setIsSettingsOpen(false)} />
      )}
    </div>
  );
}
