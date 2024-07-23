import React, { createContext, useContext, useState, useEffect } from 'react';
import mqtt from 'mqtt';
const DataContext = createContext(null);

export const DataProvider = ({ children }) => {
    const [systemData, setSystemData] = useState([]);
    const [websocket, setWebsocket] = useState(null);
    const [currentMeasurements, setCurrentMeasurements] = useState({
        weight: '---',
        do: '---',
        ph: '---',
        temp: '---',
        expected_weight: "---",
        buffer_weight: "---",
        lysate_weight: "---"
    });
    const [pumpData, setPumpData] = useState({});
    const [configData, setConfigData] = useState({});

    useEffect(() => {
        // Create a new WebSocket connection when the component mounts
        const ws = new WebSocket("ws://localhost:8765");
    
        ws.onopen = () => {
            console.log("WebSocket connection established");
            // Send a 'ping' message at regular intervals
            const pingInterval = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: "ping" }));
                }
            }, 20000);
    
            // Clear the interval on WebSocket close
            ws.onclose = () => {
                clearInterval(pingInterval);
                console.log("WebSocket connection closed");
            };
        };
    
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'button_setup':
                    console.log("Button setup data received:", data.data);
                    setPumpData(data.data);
                    break;
                case 'config_setup':
                    console.log("Config setup data received:", data.data);
                    setConfigData(data.data);
                    break;
                case 'pong':
                    console.log("Pong received from server");
                    break;
                default:
                    console.log("Received unknown message type:", data.type);
                    break;
            }
        };
    
        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    
        // Store the WebSocket connection in state
        setWebsocket(ws);
    
        // Cleanup function to close WebSocket connection when the component unmounts
        return () => {
            console.log("Closing WebSocket");
            ws.close();
        };
    }, []); // Empty dependency array ensures this runs only once on mount
    useEffect(() => {
        // MQTT connection setup
        const client = mqtt.connect('ws://192.168.0.25:9001');

        client.on('connect', () => {
            console.log('Connected to MQTT broker');
            client.subscribe('sensor_data');
        });

        client.on('message', (topic, message) => {
            if (topic === 'sensor_data') {
                const data = JSON.parse(message.toString());
                console.log("MQTT Data Received:", data);
                setSystemData(prevData => [...prevData, data]);
                setCurrentMeasurements({
                    weight: data.feed_weight,
                    do: data.do,
                    ph: data.ph,
                    temp: data.temp,
                    expected_weight: data.lactose_weight,
                    buffer_weight: data.buffer_weight,
                    lysate_weight: data.lysate_weight
                });
            }
        });

        client.on('error', (error) => {
            console.error("MQTT error:", error);
        });

        // Cleanup function to close MQTT connection when the component unmounts
        return () => {
            console.log("Closing MQTT connection");
            client.end();
        };
    }, []); // Empty dependency array ensures this runs only once on mount
    
    return (
        <DataContext.Provider value={{ systemData, currentMeasurements, websocket, pumpData, configData }}>
            {children}
        </DataContext.Provider>
    );
};

export const useData = () => useContext(DataContext);