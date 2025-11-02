import React, { useEffect, useMemo, useState } from 'react';
import api from '../../utils/api';

interface LocalSubmission {
  id: string | number;
  title: string;
  description: string;
  location?: string;
  contact_info?: string;
  latitude?: number | string | null;
  longitude?: number | string | null;
  images?: { name: string; type: string; size: number }[];
  videos?: { name: string; type: string; size: number }[];
  offline?: boolean;
  saved_at?: string;
}

const MySubmissions: React.FC = () => {
  const [items, setItems] = useState<LocalSubmission[]>([]);
  const [syncingId, setSyncingId] = useState<string | number | null>(null);

  const load = () => {
    try {
      const data = JSON.parse(localStorage.getItem('local_submissions') || '[]');
      setItems(data);
    } catch {
      setItems([]);
    }
  };

  useEffect(() => { load(); }, []);

  const exportJson = () => {
    const data = localStorage.getItem('local_submissions') || '[]';
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `local_submissions_${Date.now()}.json`; a.click();
    URL.revokeObjectURL(url);
  };

  const clearAll = () => {
    if (window.confirm('Clear all locally saved submissions?')) {
      localStorage.removeItem('local_submissions');
      load();
    }
  };

  const retrySync = async (sub: LocalSubmission) => {
    try {
      setSyncingId(sub.id);
      const form = new FormData();
      form.append('title', sub.title);
      form.append('description', sub.description);
      form.append('location', sub.location || '');
      form.append('contact_info', sub.contact_info || '');
      if (sub.latitude) form.append('latitude', String(sub.latitude));
      if (sub.longitude) form.append('longitude', String(sub.longitude));
      await api.post('/api/v1/issues/report', form, { headers: { 'Content-Type': 'multipart/form-data' } });
      // Mark as synced locally
      const next = items.map(i => i.id === sub.id ? { ...i, offline: false, synced_at: new Date().toISOString() } as any : i);
      localStorage.setItem('local_submissions', JSON.stringify(next));
      setItems(next);
      alert('✅ Synced to server.');
    } catch (e: any) {
      alert(`❌ Sync failed: ${e?.response?.data?.detail || e?.message || 'Unknown error'}`);
    } finally {
      setSyncingId(null);
    }
  };

  const deleteItem = (id: string | number) => {
    if (!window.confirm('Delete this local submission?')) return;
    const next = items.filter(i => i.id !== id);
    localStorage.setItem('local_submissions', JSON.stringify(next));
    setItems(next);
  };

  return (
    <div className="min-h-screen newspaper-bg">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="newspaper-header text-center py-6 mb-6">
          <div className="border-t-4 border-b-4 border-black py-3 mx-4">
            <h1 className="newspaper-title text-4xl font-black text-black mb-1 tracking-tight">My Submissions</h1>
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <button className="btn-secondary" onClick={exportJson}>Export JSON</button>
          <button className="btn-secondary" onClick={clearAll}>Clear All</button>
          <a className="btn-primary" href="/report">Report New</a>
        </div>

        {items.length === 0 ? (
          <div className="card text-center">No local submissions found.</div>
        ) : (
          <div className="space-y-3">
            {items.slice().reverse().map((sub) => (
              <div key={sub.id} className="p-4 border border-secondary-200 rounded bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-bold">{sub.title}</div>
                    <div className="text-sm text-secondary-700">{sub.location}</div>
                    {sub.saved_at && (<div className="text-xs text-secondary-500">Saved: {new Date(sub.saved_at).toLocaleString()}</div>)}
                  </div>
                  <div className="flex gap-2">
                    {sub.offline && (
                      <button
                        className="btn-primary"
                        disabled={syncingId === sub.id}
                        onClick={() => retrySync(sub)}
                      >{syncingId === sub.id ? 'Syncing...' : 'Sync Now'}</button>
                    )}
                    <button className="btn-secondary" onClick={() => deleteItem(sub.id)}>Delete</button>
                  </div>
                </div>
                <div className="mt-2 text-sm text-secondary-800 whitespace-pre-wrap">
                  {sub.description}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MySubmissions;






