import React, { createContext, useContext, useState, useEffect } from 'react';
import mqtt from 'mqtt';

const DataContext = createContext(null);

export const DataProvider = ({ children }) => {
    const [systemData, setSystemData] = useState([]);
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
        // Fetch configuration data from Flask server using fetch
        const fetchConfigData = async () => {
            try {
                const response = await fetch('/config');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const configData = await response.json();
                console.log("Config data received from Flask server:", configData);
                setConfigData(configData.sp_config);
                setPumpData(configData.pump_config);
            } catch (error) {
                console.error("Error fetching config data:", error);
            }
        };

        fetchConfigData();
    }, []);

    useEffect(() => {
        // MQTT connection setup
        const client = mqtt.connect('ws://localhost:9001', { connectTimeout: 5000 });

        client.on('connect', () => {
            console.log('Connected to MQTT broker');
            client.subscribe(['sensor_data'], (err) => {
                if (err) {
                    console.error('Subscription error:', err);
                } else {
                    console.log('Subscribed to sensor_data topic');
                }
            });
        });

        client.on('message', (topic, message) => {
            const data = JSON.parse(message.toString());
            console.log(`MQTT Message Received. Topic: ${topic}, Data: ${JSON.stringify(data)}`);
            if (topic === 'sensor_data') {
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
        <DataContext.Provider value={{ systemData, currentMeasurements, pumpData, configData }}>
            {children}
        </DataContext.Provider>
    );
};

export const useData = () => useContext(DataContext);