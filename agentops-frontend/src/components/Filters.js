import React from 'react';

const Filters = ({ filters, setFilters, handleSearch }) => {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <input
        type="text"
        placeholder="Search by agent name"
        value={filters.search || ''}
        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
      />

      <select
        onChange={(e) => setFilters({ ...filters, owner: e.target.value })}
        value={filters.owner || ''}
      >
        <option value="">All Owners</option>
        <option value="Team-A">Team-A</option>
        <option value="Team-B">Team-B</option>
        <option value="ownerX">ownerX</option>
      </select>

      <button onClick={handleSearch}>🔍 Search</button>
    </div>
  );
};

export default Filters;
