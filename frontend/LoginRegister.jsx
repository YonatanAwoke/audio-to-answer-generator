import React, { useState } from 'react';
import axios from 'axios';

const LoginRegister = ({ setUserId }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const endpoint = isLogin ? '/api/login/' : '/api/register/';
      const res = await axios.post(endpoint, null, {
        params: { username, password },
      });
      if (isLogin && res.data.user_id) {
        setUserId(res.data.user_id);
      } else if (!isLogin) {
        setIsLogin(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error');
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-8 p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-4">{isLogin ? 'Login' : 'Register'}</h2>
      <form onSubmit={handleSubmit}>
        <input
          className="w-full mb-2 p-2 border rounded"
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          className="w-full mb-2 p-2 border rounded"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <button className="w-full bg-blue-500 text-white p-2 rounded mb-2" type="submit">
          {isLogin ? 'Login' : 'Register'}
        </button>
      </form>
      <button
        className="text-blue-500 underline text-sm"
        onClick={() => { setIsLogin(!isLogin); setError(''); }}
      >
        {isLogin ? 'Need an account? Register' : 'Already have an account? Login'}
      </button>
    </div>
  );
};

export default LoginRegister;
