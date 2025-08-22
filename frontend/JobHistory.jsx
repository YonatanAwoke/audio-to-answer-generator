import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function JobHistory({ userId }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchHistory() {
      setLoading(true);
      try {
        const res = await axios.get(`/api/history/?user_id=${userId}`);
        setHistory(res.data);
      } catch (err) {
        setError('Failed to load history.');
      }
      setLoading(false);
    }
    fetchHistory();
  }, [userId]);

  return (
    <div className="max-w-xl mx-auto p-4">
      <h2 className="text-xl font-bold mb-2">Job History</h2>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      <ul>
        {history.map(job => (
          <li key={job.job_id} className="mb-2 p-2 border rounded">
            <div className="font-medium">{job.filename}</div>
            <div>Status: {job.status}</div>
            <div>Created: {job.created_at}</div>
            <div>Completed: {job.completed_at || 'N/A'}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
