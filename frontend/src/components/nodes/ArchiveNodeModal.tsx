import React, { useState } from 'react';
import { X, Trash2, AlertTriangle } from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { Node } from '../../types';

interface ArchiveNodeModalProps {
  isOpen: boolean;
  node: Node;
  onClose: () => void;
  onSuccess: () => void;
}

export const ArchiveNodeModal: React.FC<ArchiveNodeModalProps> = ({
  isOpen,
  node,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleArchive = async () => {
    setLoading(true);
    try {
      await apiClient.delete('/nodes/' + (node.node_code || node.node_id));
      onSuccess();
      onClose();
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xl max-w-sm w-full space-y-4 text-center">
        <div className="h-12 w-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="h-6 w-6" />
        </div>

        <h3 className="text-base font-bold text-slate-900">Archive Station?</h3>
        <p className="text-xs text-slate-500">
          Are you sure you want to deactivate <strong className="text-slate-800">{node.node_code || node.node_id}</strong>? Telemetry history will be preserved in audit records.
        </p>

        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-200"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleArchive}
            disabled={loading}
            className="px-4 py-2 bg-rose-600 text-white rounded-xl text-xs font-bold hover:bg-rose-700 flex items-center gap-1.5"
          >
            <Trash2 className="h-4 w-4" />
            {loading ? 'Archiving...' : 'Confirm Archive'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArchiveNodeModal;
