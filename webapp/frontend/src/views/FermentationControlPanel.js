import { Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useTogglePumpButton, useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import { useFeedPumpStatus, useBasePumpStatus, useLactosePumpStatus, useControlLoopStatus, useDataCollectionStatus, useAcidPumpStatus, useFeedMediaStatus } from '../components/StatusBoxes';
import { Chart } from '../components/Charts';
import '../App.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const FermentationControlPanel = () => {
  const { systemData, currentMeasurements } = useData();
  const fermentationLoopIdentifier = 'fermentation_loop';
  
  

  const [controlLoopButton, isControlLoopRunning] = useControlLoopButton("start_control", "stop_control", fermentationLoopIdentifier);
  const dataCollectionButton = useDataCollectionButton("start_collection", "stop_collection", fermentationLoopIdentifier, isControlLoopRunning);
  const toggleFeedPumpButton = useTogglePumpButton("Toggle Feed Pump", "toggle_feed", fermentationLoopIdentifier);
  const toggleBasePumpButton = useTogglePumpButton("Toggle Base Pump", "toggle_base", fermentationLoopIdentifier);
  const toggleLactosePumpButton = useTogglePumpButton("Toggle Lactose Pump", "toggle_lactose", fermentationLoopIdentifier);
  const toggleAcidPumpButton = useTogglePumpButton("Toggle Acid Pump", "toggle_acid", fermentationLoopIdentifier);
  const toggleFeedMediaButton = useTogglePumpButton("Switch Feed Media", "toggle_feed_media", fermentationLoopIdentifier);
  
  const feedPumpStatus = useFeedPumpStatus();
  const basePumpStatus = useBasePumpStatus();
  const lactosePumpStatus = useLactosePumpStatus();
  const controlLoopStatus = useControlLoopStatus();
  const acidPumpStatus = useAcidPumpStatus();
  const dataCollectionStatus = useDataCollectionStatus();
  const feedMediaStatus = useFeedMediaStatus();

  return (
    <div className="App container mt-5">
      <h1>Fermentaion Control Panel</h1>
      <div className="mb-3">
        <div className="button-status-container">
          {dataCollectionButton}
          {dataCollectionStatus}
        </div>
      </div>
      <Tabs defaultActiveKey="weight" id="uncontrolled-tab-example" className="mb-3">
        <Tab eventKey="weight" title="Weight">
          <h3>Feed Weight: {currentMeasurements.weight} g</h3>
          <h3>Lactose Weight: {currentMeasurements.expected_weight} g</h3>
          <Chart systemData={systemData} label="Feed_Weight" actualColor="rgb(75, 192, 192)"
          expectedDataKey="lactose_weight" expectedColor="rgb(255, 99, 132)" />
        </Tab>
        <Tab eventKey="do" title="DO">
          <h3>DO: {currentMeasurements.do} %</h3>
          <Chart systemData={systemData} label="do" color="rgb(75, 192, 192)" 
          expectedDataKey="do" expectedColor="rgb(75, 192, 192)"/>
        </Tab>
        <Tab eventKey="temp" title="Temperature">
          <h3>Temp: {currentMeasurements.temp} °C</h3>
          <Chart systemData={systemData} label="Temperature" color="rgb(75, 192, 192)" 
          expectedDataKey="Temperature" expectedColor="rgb(75, 192, 192)"/>
        </Tab>
        <Tab eventKey="ph" title="pH">
          <div className="mb-3">
            <h3>pH: {currentMeasurements.ph}</h3>
          </div>
          <Chart systemData={systemData} label="PH" color="rgb(75, 192, 192)" 
          expectedDataKey="PH" expectedColor="rgb(75, 192, 192)"/>
        </Tab>
      </Tabs>

      <div className="right-aligned-buttons">
        <div className="mb-3">
          <div className="button-status-container">
            {toggleFeedPumpButton}
            {feedPumpStatus}
          </div>
          <div className="button-status-container">
            {toggleLactosePumpButton}
            {lactosePumpStatus}
          </div>
          <div className="button-status-container">
            {toggleBasePumpButton}
            {basePumpStatus}
          </div>
          <div className="button-status-container">
            {toggleAcidPumpButton}
            {acidPumpStatus}
          </div>
          <div className="button-status-container">
            {controlLoopButton}
            {controlLoopStatus}
          </div>
          <div className="button-status-container">
            {toggleFeedMediaButton}
            {feedMediaStatus}
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default FermentationControlPanel;
