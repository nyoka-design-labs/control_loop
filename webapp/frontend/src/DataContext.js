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
      

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8765");
        ws.onopen = () => console.log("WebSocket connection established");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Data Recieved:", data);
            if (data.type === 'data') {
                setSystemData(prevData => [...prevData, data]);
                setCurrentMeasurements({
                    weight: data.feed_weight,
                    do: data.do,
                    ph: data.ph,
                    temp: data.temp,
                    expected_weight: data.expected_weight,
                    buffer_weight: data.buffer_weight,
                    lysate_weight: data.lysate_weight
                    
                  });
            }
        };
        ws.onclose = () => console.log("WebSocket connection closed");
        setWebsocket(ws);
        return () => ws.close();
    }, []);

    return (
        <DataContext.Provider value={{ systemData, currentMeasurements, websocket }}>
            {children}
        </DataContext.Provider>
    );
};

export const useData = () => useContext(DataContext);
