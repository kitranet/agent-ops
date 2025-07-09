// components/AddAgentForm.js
import React, { useState } from 'react';
import axios from 'axios';

const AddAgentForm = ({ onAgentAdded }) => {
  const [formData, setFormData] = useState({
    agent_id: '',
    agent_name: '',
    status: 'active',
    owner: '',
    agent_type: '',
    framework: '',
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://127.0.0.1:8000/agents/register', formData);
      setMessage('✅ Agent registered successfully!');
      setFormData({ agent_id: '', agent_name: '', status: 'active', owner: '', agent_type: '', framework: '' });
      onAgentAdded(); // Refresh list
    } catch (err) {
      setMessage('❌ Failed to register agent');
    }
  };

  return (
    <div style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
      <h3>➕ Register New Agent</h3>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '10px' }}>
        <input name="agent_id" placeholder="Agent ID" value={formData.agent_id} onChange={handleChange} required />
        <input name="agent_name" placeholder="Agent Name" value={formData.agent_name} onChange={handleChange} required />
        <input name="owner" placeholder="Owner" value={formData.owner} onChange={handleChange} />
        <input name="agent_type" placeholder="Agent Type" value={formData.agent_type} onChange={handleChange} />
        <input name="framework" placeholder="Framework" value={formData.framework} onChange={handleChange} />
        <select name="status" value={formData.status} onChange={handleChange}>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="maintenance">Maintenance</option>
          <option value="retired">Retired</option>
        </select>
        <button type="submit">Register Agent</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default AddAgentForm;
