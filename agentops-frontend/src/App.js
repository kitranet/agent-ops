import React, { useEffect, useState } from 'react';
import AgentTable from './components/AgentTable';
import ExportButton from './components/ExportButton';
import { fetchAllAgents } from './api/agentApi';
import AddAgentForm from './components/AddAgentForm';


function App() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('deployed_at');
  const [sortOrder, setSortOrder] = useState('desc');

  const [status, setStatus] = useState('');
  const [owner, setOwner] = useState('');
  const [framework, setFramework] = useState('');

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const [visibleColumns, setVisibleColumns] = useState({
    agent_id: true,
    agent_name: true,
    status: true,
    owner: true,
    agent_type: true,
    framework: true,
    health: true,
    deployed_at: true,
  });

  const fetchData = () => {
    setLoading(true);
    fetchAllAgents({
      search,
      sort_by: sortBy,
      sort_order: sortOrder,
      status,
      owner,
      framework,
      skip: (currentPage - 1) * itemsPerPage,
      limit: itemsPerPage
    })
      .then(data => {
        setAgents(data.active_agents.concat(data.archived_agents));
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, [search, sortBy, sortOrder, status, owner, framework, currentPage]);

  const handleColumnToggle = (col) => {
    setVisibleColumns(prev => ({
      ...prev,
      [col]: !prev[col]
    }));
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>AgentOps Dashboard</h1>

      {/* 🔍 Search */}
      <div style={{ marginBottom: '10px' }}>
        🔍 <input
          type="text"
          placeholder="Search by name"
          value={search}
          onChange={e => {
            setSearch(e.target.value);
            setCurrentPage(1);
          }}
        />
      </div>

      {/* 🔄 Filters */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <select value={status} onChange={e => {
          setStatus(e.target.value);
          setCurrentPage(1);
        }}>
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="maintenance">Maintenance</option>
        </select>

        <select value={owner} onChange={e => {
          setOwner(e.target.value);
          setCurrentPage(1);
        }}>
          <option value="">All Owners</option>
          <option value="Team-A">Team-A</option>
          <option value="Team-B">Team-B</option>
          <option value="Team-C">Team-C</option>
          <option value="Team-D">Team-D</option>
          <option value="Team-Z">Team-Z</option>
          <option value="ownerX">ownerX</option>
        </select>

        <select value={framework} onChange={e => {
          setFramework(e.target.value);
          setCurrentPage(1);
        }}>
          <option value="">All Frameworks</option>
          <option value="LangChain">LangChain</option>
          <option value="LangGraph">LangGraph</option>
          <option value="AutoGen">AutoGen</option>
        </select>
      </div>

      {/* 🧩 Column Toggles */}
      <div style={{ marginBottom: '10px' }}>
        {Object.keys(visibleColumns).map(col => (
          <label key={col} style={{ marginRight: '10px' }}>
            <input
              type="checkbox"
              checked={visibleColumns[col]}
              onChange={() => handleColumnToggle(col)}
            />
            {col.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </label>
        ))}
      </div>
      {/* ➕ Add Agent Form */}
<AddAgentForm onAgentAdded={fetchData} />


      {/* 📤 Export */}
      <ExportButton />

      {/* 📊 Table */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <AgentTable
            agents={agents}
            onSortChange={(col) => {
              setSortBy(col);
              setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
              setCurrentPage(1);
            }}
            visibleColumns={visibleColumns}
          />

          {/* 📄 Pagination */}
          <div style={{ marginTop: '10px' }}>
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => prev - 1)}
            >
              ⬅ Previous
            </button>
            <span style={{ margin: '0 10px' }}>Page {currentPage}</span>
            <button onClick={() => setCurrentPage(prev => prev + 1)}>
              Next ➡
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
