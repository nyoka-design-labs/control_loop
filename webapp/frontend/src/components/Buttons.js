import React, { useState, useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { useData } from '../DataContext'; // Use the custom hook


export const useControlLoopButton = (startCommand, stopCommand, loopIdentifier) => {
  const [isControlLoopRunning, setIsControlLoopRunning] = useState(false);
  const { websocket } = useData();

  const handleStartControlLoop = () => {
      if (!isControlLoopRunning && websocket) {
          const command = JSON.stringify({ command: startCommand, loopID: loopIdentifier });
          websocket.send(command);
          console.log(`Sending: ${command}`);
          setIsControlLoopRunning(true);
      }
  };

  const handleStopControlLoop = () => {
      if (isControlLoopRunning && websocket) {
          const command = JSON.stringify({ command: stopCommand, loopID: loopIdentifier });
          websocket.send(command);
          console.log(`Sending: ${command}`);
          setIsControlLoopRunning(false);
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

  return [controlLoopButton, isControlLoopRunning];
};

export const useDataCollectionButton = (startCommand, stopCommand, loopIdentifier, isControlLoopRunning) => {
  const [isDataCollectionRunning, setIsDataCollectionRunning] = useState(false);
  const { websocket } = useData();

  // Ensure that data collection runs when control loop is running
  useEffect(() => {
      if (isControlLoopRunning && !isDataCollectionRunning) {
          setIsDataCollectionRunning(true);
      }
  }, [isControlLoopRunning, isDataCollectionRunning]);

  const handleStartDataCollection = () => {
      if (!isDataCollectionRunning && websocket) {
          const command = JSON.stringify({ command: startCommand, loopID: loopIdentifier });
          websocket.send(command);
          console.log(`Sending: ${command}`);
          setIsDataCollectionRunning(true);
      }
  };

  const handleStopDataCollection = () => {
      // Prevent stopping data collection when control loop is running
      if (isDataCollectionRunning && !isControlLoopRunning && websocket) {
          const command = JSON.stringify({ command: stopCommand, loopID: loopIdentifier });
          websocket.send(command);
          console.log(`Sending: ${command}`);
          setIsDataCollectionRunning(false);
      }
  };

  const dataCollectionButton = isDataCollectionRunning ? (
      <Button variant="danger" onClick={handleStopDataCollection} className="me-2" disabled={isControlLoopRunning}>
          Stop Data Collection
      </Button>
  ) : (
      <Button variant="success" onClick={handleStartDataCollection} className="me-2">
          Start Data Collection
      </Button>
  );

  return dataCollectionButton;
};

  export const useTogglePumpButton = (buttonLabel, sendCommand, loopIdentifier) => {
    const { websocket } = useData();

    const handleToggle = () => {
        if (websocket) {
          const command = JSON.stringify({ command: sendCommand, loopID: loopIdentifier });
          websocket.send(command);
          console.log(`Sending: ${command}`);
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