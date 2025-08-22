import React, { useState } from 'react';
import LoginRegister from './LoginRegister';
import AudioUpload from './AudioUpload';
import JobHistory from './JobHistory';

const App = () => {
  const [userId, setUserId] = useState(null);

  if (!userId) {
    return <LoginRegister setUserId={setUserId} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Audio to Answer Generator</h1>
        <button className="mb-4 text-blue-500 underline" onClick={() => setUserId(null)}>
          Logout
        </button>
        <AudioUpload userId={userId} />
        <JobHistory userId={userId} />
      </div>
    </div>
  );
};

export default App;
