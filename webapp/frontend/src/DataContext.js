import React, { createContext, useContext, useState, useEffect } from 'react';

const DataContext = createContext(null);

export const DataProvider = ({ children }) => {
    const [systemData, setSystemData] = useState([]);
    const [websocket, setWebsocket] = useState(null);
    const [currentMeasurements, setCurrentMeasurements] = useState({
        weight: '---',
        do: '---',
        ph: '---',
        temp: '---'
      });
      

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8765");
        ws.onopen = () => console.log("WebSocket connection established");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'data') {
                setSystemData(prevData => [...prevData, data]);
                setCurrentMeasurements({
                    weight: data.weight,
                    do: data.do,
                    ph: data.ph,
                    temp: data.temp
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
