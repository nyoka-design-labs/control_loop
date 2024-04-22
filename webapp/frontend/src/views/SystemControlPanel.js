import React, { useState, useEffect } from 'react';
import { Button, Tab, Tabs } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import { useData } from '../DataContext';
import { useControlLoopButton, useDataCollectionButton, useToggleFeedPumpButton, useToggleBasePumpButton } from '../components/Buttons';
import { useFeedPumpStatus, useBasePumpStatus, useControlLoopStatus, useDataCollectionStatus } from '../components/StatusBoxes';
import { Chart } from '../components/Charts';
import '../App.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const SystemControlPanel = () => {
  const { websocket, systemData, currentMeasurements } = useData();
  
  const controlLoopButton = useControlLoopButton();
  const dataCollectionButton = useDataCollectionButton();
  const toggleFeedPumpButton = useToggleFeedPumpButton();
  const toggleBasePumpButton = useToggleBasePumpButton();

  const feedPumpStatus = useFeedPumpStatus();
  const basePumpStatus = useBasePumpStatus();
  const controlLoopStatus = useControlLoopStatus();
  const dataCollectionStatus = useDataCollectionStatus();

  const tarePH = () => {
    const phValue = document.getElementById('ph').value;
    websocket && websocket.send(`tare_ph:${phValue}`);
  };

  return (
    <div className="App container mt-5">
      <h1>System Control Panel</h1>
      <div className="mb-3">
        <div className="button-status-container">
          {dataCollectionButton}
          {dataCollectionStatus}
        </div>
      </div>
      <Tabs defaultActiveKey="weight" id="uncontrolled-tab-example" className="mb-3">
        <Tab eventKey="weight" title="Weight">
          <h3>Weight: {currentMeasurements.weight} g</h3>
          <Chart systemData={systemData} label="Weight" color="rgb(75, 192, 192)" />
        </Tab>
        <Tab eventKey="do" title="DO">
          <h3>DO: {currentMeasurements.do} %</h3>
          <Chart systemData={systemData} label="Weight" color="rgb(75, 192, 192)" />
        </Tab>
        <Tab eventKey="temp" title="Temperature">
          <h3>Temp: {currentMeasurements.temp} °C</h3>
          <Chart systemData={systemData} label="Temperature" color="rgb(75, 192, 192)" />
        </Tab>
        <Tab eventKey="ph" title="pH">
          <div className="mb-3">
            <h3>pH: {currentMeasurements.ph}</h3>
            
            <input type='text' id='ph'/>
            <Button variant="primary" onClick={tarePH} className="custom-padding">Tare pH</Button>
          </div>
          <Chart systemData={systemData} label="PH" color="rgb(75, 192, 192)" />
        </Tab>
      </Tabs>

      <div className="right-aligned-buttons">
        <div className="mb-3">
          <div className="button-status-container">
            {toggleFeedPumpButton}
            {feedPumpStatus}
          </div>
          <div className="button-status-container">
            {toggleBasePumpButton}
            {basePumpStatus}
          </div>
           <div className="button-status-container">
            {controlLoopButton}
            {controlLoopStatus}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemControlPanel;
