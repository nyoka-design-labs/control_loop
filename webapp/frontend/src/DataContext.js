import React, { createContext, useContext, useState, useEffect } from 'react';

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

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8765");

        ws.onopen = () => {
            console.log("WebSocket connection established");
            
            // Send a ping message every 20 seconds to keep the connection alive
            const pingInterval = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: "ping" }));
                }
            }, 20000);

            // Clear the interval on close
            ws.onclose = () => {
                clearInterval(pingInterval);
                console.log("WebSocket connection closed");
            };
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'data') {
                console.log("Data Received:", data);
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

            if (data.type === 'button_setup') {
                console.log("Button setup data received:", data.data);
                setPumpData(data.data);
            }

            // Handle pong response
            if (data.type === 'pong') {
                console.log("Pong received from server");
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        setWebsocket(ws);
        return () => ws.close();
    }, []);

    return (
        <DataContext.Provider value={{ systemData, currentMeasurements, websocket, pumpData }}>
            {children}
        </DataContext.Provider>
    );
};

export const useData = () => useContext(DataContext);