import React, { useState, useEffect } from 'react';
import { Button } from 'react-bootstrap';
import mqtt from 'mqtt';

// MQTT Client Setup
const brokerAddress = '192.168.0.25'; // Change to your broker address if needed
const port = 1883;
const clientId = `mqttjs_${Math.random().toString(16).substr(2, 8)}`;

const mqttClient = mqtt.connect(`mqtt://${brokerAddress}:${port}`, {
    clientId: clientId
});

mqttClient.on('connect', () => {
    console.log('Connected to MQTT Broker');
});

mqttClient.on('error', (err) => {
    console.error('MQTT Connection Error:', err);
});

export const useControlLoopButton = (startCommand, stopCommand, loopIdentifier) => {
    const [isControlLoopRunning, setIsControlLoopRunning] = useState(false);

    const handleStartControlLoop = () => {
        if (!isControlLoopRunning && mqttClient) {
            const command = JSON.stringify({ command: startCommand, loopID: loopIdentifier });
            mqttClient.publish('commands', command);
            console.log(`Publishing: ${command} to topic 'commands'`);
            setIsControlLoopRunning(true);
        }
    };

    const handleStopControlLoop = () => {
        if (isControlLoopRunning && mqttClient) {
            const command = JSON.stringify({ command: stopCommand, loopID: loopIdentifier });
            mqttClient.publish('commands', command);
            console.log(`Publishing: ${command} to topic 'commands'`);
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

    useEffect(() => {
        if (isControlLoopRunning && !isDataCollectionRunning) {
            setIsDataCollectionRunning(true);
        }
    }, [isControlLoopRunning, isDataCollectionRunning]);

    const handleStartDataCollection = () => {
        if (!isDataCollectionRunning && mqttClient) {
            const command = JSON.stringify({ command: startCommand, loopID: loopIdentifier });
            mqttClient.publish('commands', command);
            console.log(`Publishing: ${command} to topic 'commands'`);
            setIsDataCollectionRunning(true);
        }
    };

    const handleStopDataCollection = () => {
        if (isDataCollectionRunning && !isControlLoopRunning && mqttClient) {
            const command = JSON.stringify({ command: stopCommand, loopID: loopIdentifier });
            mqttClient.publish('commands', command);
            console.log(`Publishing: ${command} to topic 'commands'`);
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
    const handleToggle = () => {
        if (mqttClient) {
            const command = JSON.stringify({ command: sendCommand, loopID: loopIdentifier });
            mqttClient.publish('commands', command);
            console.log(`Publishing: ${command} to topic 'commands'`);
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

    const toggleState = () => {
        const commandToSend = isRunning ? sendCommandOff : sendCommandOn;
        if (mqttClient) {
            mqttClient.publish('commands', commandToSend);
            console.log(`Publishing: ${commandToSend} to topic 'commands'`);
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