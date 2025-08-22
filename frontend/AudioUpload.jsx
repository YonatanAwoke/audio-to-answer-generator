import React, { useState } from 'react';
import axios from 'axios';

export default function AudioUpload({ userId }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const uploadRes = await axios.post(`/api/upload-audio/?user_id=${userId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus('Processing...');
      const jobId = uploadRes.data.job_id;
      // Poll for result
      let pollCount = 0;
      while (pollCount < 60) {
        const res = await axios.get(`/api/result/${jobId}`);
        if (res.data.status === 'done') {
          setResult(res.data);
          setStatus('Done');
          break;
        }
        await new Promise((r) => setTimeout(r, 2000));
        pollCount++;
      }
      if (pollCount === 60) setStatus('Timed out.');
    } catch (err) {
      setStatus('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Audio to Answer</h1>
      <input type="file" accept="audio/*" onChange={handleFileChange} className="mb-2" />
      <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded mb-4">Upload</button>
      <div className="mb-2">{status}</div>
      {result && (
        <div className="bg-gray-100 p-4 rounded">
          <h2 className="font-semibold">Transcript</h2>
          <pre className="mb-2 whitespace-pre-wrap">{result.transcript}</pre>
          <h2 className="font-semibold">Questions & Answers</h2>
          {result.questions?.map((q, i) => (
            <div key={q.id} className="mb-2">
              <div className="font-medium">Q{i+1}: {q.question}</div>
              <div className="ml-4">A: {result.answers?.find(a => a.qid === q.id)?.answer}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
