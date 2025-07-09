import React from 'react';
import '../styles/table.css';

const AgentTable = ({ agents, onSortChange, visibleColumns }) => {
  const renderHeader = (label, field) =>
    visibleColumns[field] && (
      <th
        onClick={() => onSortChange(field)}
        style={{ cursor: 'pointer', userSelect: 'none' }}
      >
        {label} ⬍
      </th>
    );

  const renderStatus = (status) => {
    const statusMap = {
      active: '🟢 Active',
      inactive: '🔴 Inactive',
      maintenance: '🟡 Maintenance',
      retired: '⚫ Retired',
    };
    return statusMap[status?.toLowerCase()] || `⚪ ${status}`;
  };

  return (
    <table>
      <thead>
        <tr>
          {visibleColumns.agent_id && <th>Agent ID</th>}
          {renderHeader('Name', 'agent_name')}
          {renderHeader('Status', 'status')}
          {renderHeader('Owner', 'owner')}
          {renderHeader('Type', 'agent_type')}
          {renderHeader('Framework', 'framework')}
          {visibleColumns.health && <th>Health</th>}
          {renderHeader('Deployed At', 'deployed_at')}
        </tr>
      </thead>
      <tbody>
        {agents.map(agent => (
          <tr key={agent.agent_id}>
            {visibleColumns.agent_id && <td>{agent.agent_id}</td>}
            {visibleColumns.agent_name && <td>{agent.agent_name}</td>}
            {visibleColumns.status && <td>{renderStatus(agent.status)}</td>}
            {visibleColumns.owner && <td>{agent.owner}</td>}
            {visibleColumns.agent_type && <td>{agent.agent_type}</td>}
            {visibleColumns.framework && <td>{agent.framework}</td>}
            {visibleColumns.health && <td>{agent.health}</td>}
            {visibleColumns.deployed_at && <td>{agent.deployed_at}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AgentTable;
