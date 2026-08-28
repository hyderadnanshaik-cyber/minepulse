import React, { useState, useEffect, useCallback } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { StatusBar } from './StatusBar';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
import { BottomNav } from './BottomNav';
import { SubsidenceAlertModal } from '../ui/SubsidenceAlertModal';
import { ProductTourModal } from '../onboarding/ProductTourModal';
import { useAlertStore } from '../../store/alertStore';
import { apiClient } from '../../services/api/apiClient';

export const AppLayout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [tourOpen, setTourOpen] = useState(false);
  const [modalAlert, setModalAlert] = useState<{
    nodeId?: string;
    panel?: string;
    displacement?: number;
    tilt?: number;
    crackWidth?: number;
    severity?: string;
    message?: string;
    triggeredAt?: string;
    alertId?: number;
    affectedInfrastructure?: any[];
  } | null>(null);
  const [shownAlertIds, setShownAlertIds] = useState<Set<number>>(new Set());

  const navigate = useNavigate();
  const { addAlert } = useAlertStore();

  useEffect(() => {
    const tourCompleted = localStorage.getItem('strata_tour_completed');
    if (!tourCompleted) {
      const tourTimer = setTimeout(() => {
        setTourOpen(true);
      }, 1500);
      return () => clearTimeout(tourTimer);
    }
  }, []);

  useEffect(() => {
    const checkAlerts = async () => {
      try {
        const res = await apiClient.get('/alerts?limit=10&status=DETECTED,ACTIVE');
        const incoming = Array.isArray(res.data) ? res.data : (res.data?.alerts ?? []);
        
        let activeImpactInfra: any[] = [];
        const hasCritical = incoming.some((a: any) => 
          (a.severity === 'CRITICAL' || a.severity === 'HIGH') &&
          (a.status === 'DETECTED' || a.status === 'ACTIVE') &&
          !shownAlertIds.has(a.id)
        );

        if (hasCritical) {
          try {
            const impactRes = await apiClient.get('/infrastructure/gis/impact');
            activeImpactInfra = impactRes.data?.affected_infrastructure || [];
          } catch {}
        }

        incoming.forEach((a: any) => {
          addAlert(a);
          if (
            (a.severity === 'CRITICAL' || a.severity === 'HIGH') &&
            (a.status === 'DETECTED' || a.status === 'ACTIVE') &&
            !shownAlertIds.has(a.id)
          ) {
            setShownAlertIds((prev) => new Set(prev).add(a.id));
            setModalAlert({
              alertId: a.id,
              nodeId: a.node_code || a.node_id || 'NODE-03',
              panel: a.panel ?? 'Panel Alpha North',
              displacement: a.displacement ?? undefined,
              tilt: a.tilt ?? undefined,
              crackWidth: a.crack_width ?? undefined,
              severity: a.severity,
              message: a.message ?? a.title,
              triggeredAt: a.detected_at ?? a.triggered_at,
              affectedInfrastructure: activeImpactInfra,
            });
            setModalOpen(true);
          }
        });
      } catch {
        // Best-effort
      }
    };

    const timer = setInterval(checkAlerts, 8000);
    return () => clearInterval(timer);
  }, [shownAlertIds, addAlert]);

  const handleModalAcknowledge = useCallback(async () => {
    if (!modalAlert?.alertId) {
      setModalOpen(false);
      return;
    }
    try {
      await apiClient.post('/alerts/' + modalAlert.alertId + '/acknowledge', {
        notes: 'Acknowledged from Emergency Modal',
      });
    } catch {
      // Best-effort
    }
    setModalOpen(false);
  }, [modalAlert]);

  const handleModalViewGIS = useCallback(() => {
    setModalOpen(false);
    navigate('/app/gis');
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col antialiased font-sans overflow-x-hidden">
      <StatusBar />
      <div className="flex flex-1 min-h-0 relative">
        {/* Mobile overlay backdrop — closes sidebar when tapping outside */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/40 z-20 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
            aria-hidden="true"
          />
        )}
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <div className="flex-1 flex flex-col min-w-0 lg:pl-64 rtl:lg:pl-0 rtl:lg:pr-64 transition-all duration-200 overflow-x-hidden">
          <TopBar
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
            onOpenTour={() => setTourOpen(true)}
          />
          <main className="flex-1 p-3 sm:p-5 lg:p-8 pb-24 md:pb-8 overflow-y-auto overflow-x-hidden">
            <Outlet />
          </main>
        </div>
      </div>

      {/* Mobile Bottom Navigation (Visible on <768px screens) */}
      <BottomNav />

      {/* Global Critical Subsidence Alert Modal */}
      <SubsidenceAlertModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onAcknowledge={handleModalAcknowledge}
        onViewGIS={handleModalViewGIS}
        alert={modalAlert ?? undefined}
      />

      {/* Product Onboarding Tour Modal */}
      <ProductTourModal isOpen={tourOpen} onClose={() => setTourOpen(false)} />
    </div>
  );

};

export default AppLayout;
