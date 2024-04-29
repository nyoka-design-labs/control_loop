import { Button, Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useTogglePumpButton, useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import { useFeedPumpStatus, useBasePumpStatus, useControlLoopStatus, useDataCollectionStatus, useBufferPumpStatus, useLysatePumpStatus } from '../components/StatusBoxes';
import { Chart } from '../components/Charts';
import '../App.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const ConcentrationControlPanel = () => {
  const { websocket, systemData, currentMeasurements } = useData();
  
  const controlLoopButton = useControlLoopButton("start_control", "stop_control");
  const dataCollectionButton = useDataCollectionButton("start_collection", "stop_collection");
  const toggleBufferPumpButton = useTogglePumpButton("Toggle Buffer Pump", "toggle_buffer");
  const toggleLysatePumpButton = useTogglePumpButton("Toggle Lysate Pump", "toggle_lysate");

  const bufferPumpStatus = useBufferPumpStatus();
  const lysatePumpStatus = useLysatePumpStatus();
  const controlLoopStatus = useControlLoopStatus();
  const dataCollectionStatus = useDataCollectionStatus();


  return (
    <div className="App container mt-5">
      <h1>Concentration Control Panel</h1>
      <div className="mb-3">
        <div className="button-status-container">
          {dataCollectionButton}
          {dataCollectionStatus}
        </div>
      </div>
      <Tabs defaultActiveKey="buffer_weight" id="uncontrolled-tab-example" className="mb-3">
        <Tab eventKey="buffer_weight" title="Buffer Weight">
          <h3>Buffer Weight: {currentMeasurements.buffer_weight} g</h3>
          <Chart systemData={systemData} label="buffer_weight" actualColor="rgb(75, 192, 192)"
          expectedDataKey="buffer_weight" expectedColor="rgb(255, 99, 132)" />
        </Tab>
        <Tab eventKey="lysate_weight" title="Lysate Weight">
          <h3>Lysate Weight: {currentMeasurements.lysate_weight} g</h3>
          <Chart systemData={systemData} label="lysate_weight" color="rgb(75, 192, 192)" 
          expectedDataKey="lysate_weight" expectedColor="rgb(75, 192, 192)"/>
        </Tab>
        
      </Tabs>

      <div className="right-aligned-buttons">
        <div className="mb-3">
          <div className="button-status-container">
            {toggleBufferPumpButton}
            {bufferPumpStatus}
          </div>
          <div className="button-status-container">
            {toggleLysatePumpButton}
            {lysatePumpStatus}
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

export default ConcentrationControlPanel;
