import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import useStatusBox from './StatusBoxes';

const ControlButtons = ({ loopIdentifier }) => {
    const [isControlLoopRunning, setIsControlLoopRunning] = useState(false);
    const [isDataCollectionRunning, setIsDataCollectionRunning] = useState(false);

    // Handle sending commands to the Flask server
    const sendCommand = async (command) => {
        try {
            const response = await fetch('/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    loopID: loopIdentifier,
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Command sent:', data);
        } catch (error) {
            console.error('Error sending command:', error);
        }
    };

    // Handle starting the control loop
    const handleStartControlLoop = () => {
        if (!isControlLoopRunning) {
            sendCommand("start_control");
            setIsControlLoopRunning(true);
            if (!isDataCollectionRunning) {
                setIsDataCollectionRunning(true); // Ensure data collection is running
            }
        }
    };

    // Handle stopping the control loop
    const handleStopControlLoop = () => {
        if (isControlLoopRunning) {
            sendCommand("stop_control");
            setIsControlLoopRunning(false);
        }
    };

    // Handle starting data collection
    const handleStartDataCollection = () => {
        if (!isDataCollectionRunning) {
            sendCommand("start_collection");
            setIsDataCollectionRunning(true);
        }
    };

    // Handle stopping data collection
    const handleStopDataCollection = () => {
        if (isDataCollectionRunning && !isControlLoopRunning) {
            sendCommand("stop_collection");
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
        <Button variant="success" onClick={handleStartDataCollection} className="me-2" disabled={isControlLoopRunning}>
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