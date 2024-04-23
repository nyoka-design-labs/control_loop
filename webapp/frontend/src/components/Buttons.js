import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import { useData } from '../DataContext'; // Use the custom hook


const sharedState = {
    isControlLoopRunning: false,
    setIsControlLoopRunning: () => {},
    isDataCollectionRunning: false,
    setIsDataCollectionRunning: () => {}
  };

export const useControlLoopButton = () => {
    const [isControlLoopRunning, setIsControlLoopRunning] = useState(sharedState.isControlLoopRunning);
    const { websocket } = useData();

    // Update the shared state object
    sharedState.isControlLoopRunning = isControlLoopRunning;
    sharedState.setIsControlLoopRunning = setIsControlLoopRunning;

    const handleStartControlLoop = () => {
        if (!isControlLoopRunning && websocket) {
        websocket.send("start_control");
        console.log('start_control');
        setIsControlLoopRunning(true);
        sharedState.setIsDataCollectionRunning(true);
        }
    };

    const handleStopControlLoop = () => {
        if (isControlLoopRunning && websocket) {
        websocket.send("stop_control");
        console.log('stop_control');
        sharedState.setIsControlLoopRunning(false);
        }
    };

    const controlLoopButton = isControlLoopRunning ? (
        <Button variant="danger" onClick={handleStopControlLoop} className="me-2">
        Stop Control Loop
        </Button>
    ) : (
        <Button variant="success" onClick={handleStartControlLoop} className="me-2">
        Start Control Loop
        </Button>
    );

    return controlLoopButton; // Returns the button component
};

export const useDataCollectionButton = () => {
    const [isDataCollectionRunning, setIsDataCollectionRunning] = useState(sharedState.isDataCollectionRunning);
    const { websocket } = useData();

    // Update the shared state object
    sharedState.isDataCollectionRunning = isDataCollectionRunning;
    sharedState.setIsDataCollectionRunning = setIsDataCollectionRunning;
  
    const handleStartDataCollection = () => {
      if (!isDataCollectionRunning && websocket) {
        websocket.send("start_collection");
        console.log('start_collection');
        setIsDataCollectionRunning(true);
      }
    };
  
    const handleStopDataCollection = () => {
      if (isDataCollectionRunning && !sharedState.isControlLoopRunning && websocket) { // need to ensure data collection cannot be stopped when control loop is running how ot make this change
        websocket.send("stop_collection");
        console.log('stop_collection');
        setIsDataCollectionRunning(false);
      }
    };
  
    const dataCollectionButton = isDataCollectionRunning ? (
      <Button variant="danger" onClick={handleStopDataCollection} className="me-2">
        Stop Data Collection
      </Button>
    ) : (
      <Button variant="success" onClick={handleStartDataCollection} className="me-2">
        Start Data Collection
      </Button>
    );
  
    return dataCollectionButton;
  };

  export const useTogglePumpButton = (buttonLabel, sendCommand) => {
    const { websocket } = useData();

    const handleToggle = () => {
        if (websocket) {
            websocket.send(sendCommand);
            console.log(sendCommand);
        }
    };

    const togglePumpButton = (
        <Button variant="secondary" onClick={handleToggle} className="me-2">
            {buttonLabel}
        </Button>
    );

    return togglePumpButton;
};

export const useStateToggleButton = (buttonLabelOn, buttonLabelOff, sendCommandOn, sendCommandOff, defaultRunningState = false) => {
  const [isRunning, setIsRunning] = useState(defaultRunningState);
  const { websocket } = useData();

  const toggleState = () => {
      const commandToSend = isRunning ? sendCommandOff : sendCommandOn;
      if (websocket) {
          websocket.send(commandToSend);
          console.log(commandToSend);
          setIsRunning(!isRunning);
      }
  };

  return (
      <Button
          variant={isRunning ? "danger" : "success"}
          onClick={toggleState}
          className="me-2">
          {isRunning ? buttonLabelOff : buttonLabelOn}
      </Button>
  );
};