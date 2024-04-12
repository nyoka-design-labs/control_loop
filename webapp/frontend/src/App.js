import React, { useState, useEffect } from 'react';
import { Button, Tabs, Tab } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto'; // Necessary for Chart.js v3 and react-chartjs-2
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [currentWeight, setCurrentWeight] = useState('---');
  const [currentDO, setCurrentDO] = useState('---')
  const [currentPH, setCurrentPH] = useState('---')
  const [currentTemp, setCurrentTemp] = useState('---')
  const [weightData, setWeightData] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:8765");
    setWs(websocket);

    websocket.onopen = () => console.log("WebSocket connection established");
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data); // Assuming server sends JSON with weight and time
      console.log("Message from server:", data);
      setCurrentWeight(`${data.weight} g`); // Update currentWeight state
      setCurrentDO(data.do)
      setCurrentPH(data.ph)
      setCurrentTemp(data.temp)
      setWeightData((prevData) => [...prevData, data]); // Append new weight data for chart
    };
    websocket.onclose = () => console.log("WebSocket connection closed");

    return () => websocket.close();
  }, []);

  const handleStartPump = () => {
    if (ws) {
      ws.send("start_pump");
      console.log("Start pump command sent");
    }
  };

  const chartData = {
    labels: weightData.map((data) => data.time), // Use the time from each data point as labels
    datasets: [
      {
        label: 'Weight Over Time',
        data: weightData.map((data) => data.weight),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const doData = {
    labels: weightData.map((data) => data.time), // Use the time from each data point as labels
    datasets: [
      {
        label: 'Weight Over Time',
        data: weightData.map((data) => data.do),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const tempData = {
    labels: weightData.map((data) => data.time), // Use the time from each data point as labels
    datasets: [
      {
        label: 'Weight Over Time',
        data: weightData.map((data) => data.temp),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const phData = {
    labels: weightData.map((data) => data.time), // Use the time from each data point as labels
    datasets: [
      {
        label: 'Weight Over Time',
        data: weightData.map((data) => data.ph),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    plugins: {
      legend: {
        display: false, // Disable toggling visibility
      }
    }
  };

  const handleStopPump = () => {
    if (ws) {
      ws.send("stop_pump");
      console.log("Stop pump command sent");
    }
  };

  const handleShowWeight = () => {
    if (ws) {
      ws.send("show_weight");
      console.log("Show weight command sent");
    }
  };
  const handleHideWeight = () => {
    if (ws) {
      ws.send("hide_weight");
      console.log("Hide weight command sent");
    }
  };

  return (
    <div className="App container mt-5">
      <h1>Scale Control Panel</h1>
      <div className="mb-3">
        <Button variant="success" onClick={handleStartPump} className="me-2">Start Pump</Button>
        <Button variant="danger" onClick={handleStopPump} className="me-2">Stop Pump</Button>
        <Button variant="info" onClick={handleShowWeight} className="me-2">Show Weight</Button>
        <Button variant="secondary" onClick={handleHideWeight} className="me-2">Stop Weight</Button>
      </div>
      <Tabs defaultActiveKey="weight" id="uncontrolled-tab-example" className="mb-3">
        <Tab eventKey="weight" title="Current Weight">
          <h3>{currentWeight}</h3>
          <Line data={chartData} options={chartOptions} />
        </Tab>
        <tab eventKey="do" title="DO">
          <h3>DO: {currentDO}%</h3>
          <Line data={doData} options={chartOptions} />
        </tab>
        <tab eventKey="temp" title="Temperature">
          <h3>Temperature: {currentTemp} deg C</h3>
          <Line data={tempData} options={chartOptions} />
        </tab>
        <tab eventKey="ph" title="pH">
          <h3>pH: {currentPH}</h3>
          <Line data={phData} options={chartOptions} />
        </tab>
      </Tabs>
    </div>
  );
}

export default App;
