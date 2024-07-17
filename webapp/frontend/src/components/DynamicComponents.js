import React from 'react';
import { useTogglePumpButton } from './Buttons';
import useStatusBox from './StatusBoxes';  // Adjust the path according to your file structure

const DynamicComponent = ({ pumpKey, loopIdentifier }) => {
  const statusKey = `${pumpKey}_status`;
  const buttonLabel = `Toggle ${pumpKey.replace(/_/g, ' ')}`;
  const toggleButton = useTogglePumpButton(buttonLabel, `toggle_${pumpKey}`, loopIdentifier);
  const statusBox = useStatusBox(statusKey, "ON", "OFF");

  return (
    <div className="button-status-container-dark">
      {toggleButton}
      {statusBox}
    </div>
  );
};

const DynamicComponents = ({ pumps, loopIdentifier }) => {
  return (
    <>
      {Object.keys(pumps).map((pumpKey) => (
        <DynamicComponent key={pumpKey} pumpKey={pumpKey} loopIdentifier={loopIdentifier} />
      ))}
    </>
  );
};

export default DynamicComponents;