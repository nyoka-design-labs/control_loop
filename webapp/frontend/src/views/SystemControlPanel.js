import React, { useState, useEffect } from 'react';
import { Button, Tab, Tabs } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import { useData } from '../DataContext';
import '../App.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const SystemControlPanel = () => {
  const { websocket, systemData } = useData();
  const [currentWeight, setCurrentWeight] = useState('---');
  const [currentDO, setCurrentDO] = useState('---');
  const [currentPH, setCurrentPH] = useState('---');
  const [currentTemp, setCurrentTemp] = useState('---');

  // WebSocket message handler setup
  useEffect(() => {
    const handleMessage = (event) => {
      const data = JSON.parse(event.data);
      setCurrentWeight(`${data.weight} g`);
      setCurrentDO(`${data.do}%`);
      setCurrentPH(data.ph);
      setCurrentTemp(`${data.temp} °C`);
    };

    if (websocket) {
      websocket.addEventListener('message', handleMessage);
    }

    return () => {
      if (websocket) {
        websocket.removeEventListener('message', handleMessage);
      }
    };
  }, [websocket]);  // Dependency on the websocket connection

  // Utility function to create chart data based on the type
  const createChartData = (label, color) => ({
    labels: systemData.map(data => data.time),
    datasets: [{
      label: `${label} Over Time`,
      data: systemData.map(data => data[label.toLowerCase()]),
      borderColor: color,
      fill: false,
      tension: 0.1
    }],
  });

  // Handlers for WebSocket commands
  const handleFeedPumpToggle = () => {
    websocket && websocket.send("start_pump");
    console.log('start_pump');
  };

  const handleBasePumpToggle = () => {
    websocket && websocket.send("stop_pump");
    console.log('stop_pump');
  };

  const handleStartControlLoop = () => {
    websocket && websocket.send("start_control");
    console.log('start_control');
  };

  const handleStopControlLoop = () => {
    websocket && websocket.send("stop_control");
    console.log('stop_control');
  };

  const handleStartDataCollection = () => {
    websocket && websocket.send("start_collection");
    console.log('start_collection');
  };

  const tarePH = () => {
    const phValue = document.getElementById('ph').value;
    websocket && websocket.send(`tare_ph:${phValue}`);
  };

  const chartOptions = {
    plugins: {
      legend: {
        display: false
      }
    }
  };

  return (
    <div className="App container mt-5">
      <h1>System Control Panel</h1>
      <div className="mb-3">
        <Button variant="success" onClick={handleStartDataCollection} className="me-2">Collect Data</Button>
      </div>
      <Tabs defaultActiveKey="weight" id="uncontrolled-tab-example" className="mb-3">
        <Tab eventKey="weight" title="Weight">
          <h3>Weight: {currentWeight} g</h3>
          <Line data={createChartData('Weight', 'rgb(75, 192, 192)')} options={chartOptions} />
        </Tab>
        <Tab eventKey="do" title="DO">
          <h3>DO: {currentDO}%</h3>
          <Line data={createChartData('DO', 'rgb(75, 192, 192)')} options={chartOptions} />
        </Tab>
        <Tab eventKey="temp" title="Temperature">
          <h3>Temperature: {currentTemp} °C</h3>
          <Line data={createChartData('Temperature', 'rgb(75, 192, 192)')} options={chartOptions} />
        </Tab>
        <Tab eventKey="ph" title="pH">
          <div className="mb-3">
            <h3>pH: {currentPH}</h3>
            
            <input type='text' id='ph'/>
            <Button variant="primary" onClick={tarePH} className="custom-padding">Tare pH</Button>
          </div>
          <Line data={createChartData('PH', 'rgb(75, 192, 192)')} options={chartOptions} />
        </Tab>
      </Tabs>

      <div className="right-aligned-buttons">
        <div className="mb-3">
          <Button variant="secondary" onClick={handleFeedPumpToggle} className="me-2">Toggle Feed Pump</Button>
          <Button variant="secondary" onClick={handleBasePumpToggle} className="me-2">Toggle Base Pump</Button>
          <Button variant="success" onClick={handleStartControlLoop} className="me-2">Start Control Loop</Button>
          <Button variant="danger" onClick={handleStopControlLoop} className="me-2">Stop Control Loop</Button>
        </div>
      </div>
    </div>
  );
};

export default SystemControlPanel;
