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


export const useToggleFeedPumpButton = () => {
    const { websocket } = useData();
  
    const handleFeedPumpToggle = () => {
      if (websocket) {
        websocket.send("toggle_feed");
        console.log('toggle_feed');
      }
    };
  
    const toggleFeedPumpButton = (
      <Button variant="secondary" onClick={handleFeedPumpToggle} className="me-2">
        Toggle Feed Pump
      </Button>
    );
  
    return toggleFeedPumpButton;
  };
  
  export const useToggleBasePumpButton = () => {
    const { websocket } = useData();
  
    const handleBasePumpToggle = () => {
      if (websocket) {
        websocket.send("toggle_base");
        console.log('toggle_base');
      }
    };
  
    const toggleBasePumpButton = (
      <Button variant="secondary" onClick={handleBasePumpToggle} className="me-2">
        Toggle Base Pump
      </Button>
    );
  
    return toggleBasePumpButton;
  };