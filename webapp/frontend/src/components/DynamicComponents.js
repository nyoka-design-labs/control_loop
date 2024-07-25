import React from 'react';
import TogglePumpButton from './TogglePumpButton'; // Import the new component
import useStatusBox from './StatusBoxes';  // Adjust the path according to your file structure
import { useData } from '../DataContext'; // Import the useData hook

const DynamicComponent = ({ pumpKey, loopIdentifier }) => {
  const statusKey = `${pumpKey}_status`;
  const buttonLabel = `Toggle ${pumpKey.replace(/_/g, ' ')}`;
  const sendCommand = `toggle_${pumpKey}`;
  const statusBox = useStatusBox(statusKey, "ON", "OFF");

  return (
    <div className="button-status-container-dark">
      <TogglePumpButton buttonLabel={buttonLabel} sendCommand={sendCommand} loopIdentifier={loopIdentifier} />
      {statusBox}
    </div>
  );
};

const DynamicComponents = ({ loopIdentifier }) => {
  const { pumpData } = useData(); // Fetch pumpData from the context
  const currentPumps = pumpData[loopIdentifier] || {}; // Get current pumps based on the loopIdentifier

  return (
    <>
      {Object.keys(currentPumps).map((pumpKey) => (
        <DynamicComponent key={pumpKey} pumpKey={pumpKey} loopIdentifier={loopIdentifier} />
      ))}
    </>
  );
};

export default DynamicComponents;