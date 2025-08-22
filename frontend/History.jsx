import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function History({ userId = 1 }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      setLoading(true);
      try {
        const res = await axios.get(`/api/history/?user_id=${userId}`);
        setHistory(res.data);
      } catch (err) {
        setHistory([]);
      }
      setLoading(false);
    }
    fetchHistory();
  }, [userId]);

  return (
    <div className="max-w-xl mx-auto p-4">
      <h2 className="text-xl font-bold mb-2">Upload History</h2>
      {loading ? (
        <div>Loading...</div>
      ) : history.length === 0 ? (
        <div>No uploads yet.</div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {history.map(job => (
            <li key={job.job_id} className="py-2">
              <div className="font-medium">{job.filename}</div>
              <div>Status: {job.status}</div>
              <div>Created: {job.created_at}</div>
              <div>Completed: {job.completed_at || 'In progress'}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
