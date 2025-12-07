import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface Report {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_by: string;
  submitted_at: string;
}

const ViewReports: React.FC = () => {
  const { userRole } = useAuth();
  const navigate = useNavigate();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Redirect if not admin
    if (userRole !== 'admin') {
      navigate('/dashboard');
      return;
    }

    fetchReports();
  }, [userRole, navigate]);

  const fetchReports = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/admin/reports`);
      if (response.ok) {
        const data = await response.json();
        setReports(data);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (reportId: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/admin/reports/${reportId}/approve`, {
        method: 'PUT',
      });
      if (response.ok) {
        fetchReports(); // Refresh list
      }
    } catch (error) {
      console.error('Failed to approve report:', error);
    }
  };

  const handleReject = async (reportId: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/admin/reports/${reportId}/reject`, {
        method: 'PUT',
      });
      if (response.ok) {
        fetchReports(); // Refresh list
      }
    } catch (error) {
      console.error('Failed to reject report:', error);
    }
  };

  const handleDelete = async (reportId: string) => {
    if (!window.confirm('Are you sure you want to delete this report?')) {
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/admin/reports/${reportId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchReports(); // Refresh list
      }
    } catch (error) {
      console.error('Failed to delete report:', error);
    }
  };

  const filteredReports = reports.filter(report => {
    const matchesFilter = filter === 'all' || report.status === filter;
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-800',
      approved: 'bg-green-100 text-green-800 border-green-800',
      rejected: 'bg-red-100 text-red-800 border-red-800'
    };
    return badges[status as keyof typeof badges] || badges.pending;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-2xl font-black">LOADING REPORTS...</div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4">
      {/* Newspaper Header */}
      <div className="border-4 border-black bg-white mb-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <div className="bg-black text-white p-6 text-center">
          <h1 className="text-5xl font-black mb-2 font-serif">ADMINISTRATIVE DESK</h1>
          <p className="text-xl font-bold uppercase tracking-widest">Report Management Center</p>
        </div>
        <div className="border-t-4 border-black bg-[#f4e4c1] p-4">
          <div className="flex justify-between items-center text-sm font-bold">
            <span>📋 {filteredReports.length} REPORTS</span>
            <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {/* Search */}
        <div className="border-4 border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <label className="block text-sm font-black mb-2 uppercase">SEARCH REPORTS</label>
          <input
            type="text"
            placeholder="Search by title, description, or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border-4 border-black font-bold focus:outline-none focus:ring-4 focus:ring-black"
          />
        </div>

        {/* Status Filter */}
        <div className="border-4 border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <label className="block text-sm font-black mb-2 uppercase">FILTER BY STATUS</label>
          <div className="flex space-x-2">
            {['all', 'pending', 'approved', 'rejected'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status as any)}
                className={`flex-1 px-4 py-3 border-4 border-black font-black text-sm uppercase transition-colors ${
                  filter === status ? 'bg-black text-white' : 'bg-white text-black hover:bg-gray-100'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Reports Table */}
      <div className="border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <div className="overflow-x-auto">
          {filteredReports.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-2xl font-black mb-2">NO REPORTS FOUND</h3>
              <p className="text-gray-600 font-serif">Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-black text-white">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-black uppercase tracking-wider border-r-2 border-white">
                    REPORT DETAILS
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-black uppercase tracking-wider border-r-2 border-white">
                    CATEGORY
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-black uppercase tracking-wider border-r-2 border-white">
                    STATUS
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-black uppercase tracking-wider border-r-2 border-white">
                    SUBMITTED
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-black uppercase tracking-wider">
                    ACTIONS
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-4 border-r-2 border-black">
                      <div className="font-black text-sm mb-1">{report.title}</div>
                      <div className="text-xs text-gray-600 font-serif line-clamp-2">{report.description}</div>
                      <div className="text-xs text-gray-500 font-serif mt-1">📍 {report.location}</div>
                    </td>
                    <td className="px-4 py-4 border-r-2 border-black">
                      <span className="inline-block px-3 py-1 bg-gray-100 border-2 border-black text-xs font-black uppercase">
                        {report.category}
                      </span>
                    </td>
                    <td className="px-4 py-4 border-r-2 border-black">
                      <span className={`inline-block px-3 py-1 border-2 text-xs font-black uppercase ${getStatusBadge(report.status)}`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-4 py-4 border-r-2 border-black">
                      <div className="text-xs font-bold">{report.submitted_by}</div>
                      <div className="text-xs text-gray-500 font-serif">
                        {new Date(report.submitted_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex justify-center space-x-2">
                        {report.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(report.id)}
                              className="px-3 py-1 bg-green-500 text-white border-2 border-black font-black text-xs uppercase hover:bg-green-600 transition-colors"
                              title="Approve"
                            >
                              ✓ APPROVE
                            </button>
                            <button
                              onClick={() => handleReject(report.id)}
                              className="px-3 py-1 bg-red-500 text-white border-2 border-black font-black text-xs uppercase hover:bg-red-600 transition-colors"
                              title="Reject"
                            >
                              ✗ REJECT
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleDelete(report.id)}
                          className="px-3 py-1 bg-gray-800 text-white border-2 border-black font-black text-xs uppercase hover:bg-black transition-colors"
                          title="Delete"
                        >
                          🗑 DELETE
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mt-8">
        {[
          { label: 'TOTAL', count: reports.length, color: 'bg-gray-100' },
          { label: 'PENDING', count: reports.filter(r => r.status === 'pending').length, color: 'bg-yellow-100' },
          { label: 'APPROVED', count: reports.filter(r => r.status === 'approved').length, color: 'bg-green-100' },
          { label: 'REJECTED', count: reports.filter(r => r.status === 'rejected').length, color: 'bg-red-100' },
        ].map((stat) => (
          <div key={stat.label} className={`border-4 border-black ${stat.color} p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] text-center`}>
            <div className="text-4xl font-black mb-2">{stat.count}</div>
            <div className="text-sm font-black uppercase">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ViewReports;
