import React, { createContext, useContext, useState, useEffect } from 'react';

const DataContext = createContext(null);

export const DataProvider = ({ children }) => {
    const [systemData, setSystemData] = useState([]);
    const [websocket, setWebsocket] = useState(null);

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8765");
        ws.onopen = () => console.log("WebSocket connection established");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setSystemData(prevData => [...prevData, data]);
        };
        ws.onclose = () => console.log("WebSocket connection closed");
        setWebsocket(ws);
        return () => ws.close();
    }, []);

    return (
        <DataContext.Provider value={{ systemData, websocket }}>
            {children}
        </DataContext.Provider>
    );
};

export const useData = () => useContext(DataContext);
