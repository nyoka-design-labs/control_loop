// src/components/ControlButtons.js

import React, { useState, useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { useData } from '../DataContext'; // Use the custom hook
import useStatusBox from './StatusBoxes';

const ControlButtons = ({ loopIdentifier }) => {
    const { websocket } = useData();
    const [isControlLoopRunning, setIsControlLoopRunning] = useState(false);
    const [isDataCollectionRunning, setIsDataCollectionRunning] = useState(false);

    // Handle starting the control loop
    const handleStartControlLoop = () => {
        if (!isControlLoopRunning && websocket) {
            const command = JSON.stringify({ command: "start_control", loopID: loopIdentifier });
            websocket.send(command);
            console.log(`Sending: ${command}`);
            setIsControlLoopRunning(true);
        }
    };

    // Handle stopping the control loop
    const handleStopControlLoop = () => {
        if (isControlLoopRunning && websocket) {
            const command = JSON.stringify({ command: "stop_control", loopID: loopIdentifier });
            websocket.send(command);
            console.log(`Sending: ${command}`);
            setIsControlLoopRunning(false);
        }
    };

    // Handle starting data collection
    const handleStartDataCollection = () => {
        if (!isDataCollectionRunning && websocket) {
            const command = JSON.stringify({ command: "start_collection", loopID: loopIdentifier });
            websocket.send(command);
            console.log(`Sending: ${command}`);
            setIsDataCollectionRunning(true);
        }
    };

    // Handle stopping data collection
    const handleStopDataCollection = () => {
        if (isDataCollectionRunning && !isControlLoopRunning && websocket) {
            const command = JSON.stringify({ command: "stop_collection", loopID: loopIdentifier });
            websocket.send(command);
            console.log(`Sending: ${command}`);
            setIsDataCollectionRunning(false);
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

    const dataCollectionButton = isDataCollectionRunning ? (
        <Button variant="danger" onClick={handleStopDataCollection} className="me-2" disabled={isControlLoopRunning}>
            Stop Data Collection
        </Button>
    ) : (
        <Button variant="success" onClick={handleStartDataCollection} className="me-2">
            Start Data Collection
        </Button>
    );

    const dataCollectionStatus = useStatusBox("data_collection_status", "ON", "OFF", true);
    const controlLoopStatus = useStatusBox("control_loop_status", "ON", "OFF", true);

    return (
        <div>
            <div className="button-status-container">
                {dataCollectionButton}
                {dataCollectionStatus}
            </div>
            <div className="button-status-container">
                {controlLoopButton}
                {controlLoopStatus}
            </div>
        </div>
    );
};

export default ControlButtons;