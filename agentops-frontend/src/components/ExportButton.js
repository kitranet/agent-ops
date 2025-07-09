import React from 'react';

const ExportButton = () => {
  const handleDownload = async (format = 'csv') => {
    const response = await fetch(`http://127.0.0.1:8000/agents/export?file_format=${format}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agents_export.${format}`;
    a.click();
  };

  return (
    <div style={{ marginBottom: '10px' }}>
      <button onClick={() => handleDownload('csv')}>Export CSV</button>
      <button onClick={() => handleDownload('xlsx')}>Export Excel</button>
    </div>
  );
};

export default ExportButton;
