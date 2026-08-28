import { useState, useEffect } from 'react';
import { useSystemStore } from '../store/systemStore';
import { apiClient } from '../services/api/apiClient';

export function useConnectivity() {
  const { status, setStatus } = useSystemStore();
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await apiClient.get('/system/health');
        if (res.data) {
          setStatus({
            mesh_status: res.data.mesh_status || 'ONLINE',
            gateway_status: res.data.gateway_status || 'ONLINE',
            internet_status: isOnline ? 'ONLINE' : 'OFFLINE',
            cloud_status: res.data.cloud_status || 'ONLINE',
            db_status: res.data.db_status || 'ONLINE',
          });
        }
      } catch {
        setStatus({
          mesh_status: 'ONLINE',
          gateway_status: 'ONLINE',
          internet_status: isOnline ? 'ONLINE' : 'OFFLINE',
          cloud_status: 'ONLINE',
          db_status: 'ONLINE',
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, [isOnline, setStatus]);

  return {
    status,
    isOnline,
  };
}
