import React from 'react';
import './views.css'; // Import the views.css for styling

const Devices = () => {
  return (
    <div className="view-container">
      <h2>Devices Management</h2>
      <div className="view-content">
        <div className="graphs-section">
          <h3>Graphs</h3>
          {/* Add your graph components here */}
        </div>
        <div className="controls-section">
          <h3>Controls</h3>
          {/* Add your control components here */}
        </div>
      </div>
    </div>
  );
};

export default Devices;