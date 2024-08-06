import React, { useState, useEffect, useRef } from 'react';
import { useData } from '../DataContext';
import '../App.css';

const useStatusBox = (key, onMessage, offMessage, shouldTimeout = false) => {
    const [status, setStatus] = useState(offMessage);
    const { statusData } = useData();
    const statusTimeout = useRef();

    useEffect(() => {
        if (statusData[key] === "1" || statusData[key] === "3" || statusData[key] === "5" || statusData[key] === "7" || statusData[key] === "9" || statusData[key] === "11" || statusData[key] === "13" || statusData[key] === "15" || statusData[key] === "control_on" || statusData[key] === "data_collection_on" || statusData[key] === "Lactose") {
            clearTimeout(statusTimeout.current);
            setStatus(onMessage);
            if (shouldTimeout) {
                statusTimeout.current = setTimeout(() => {
                    setStatus(offMessage);
                }, 20000); // timeout
            }
        } else if (statusData[key] === "0" || statusData[key] === "2" || statusData[key] === "4" || statusData[key] === "6" || statusData[key] === "8" || statusData[key] === "10" || statusData[key] === "12" || statusData[key] === "14" || statusData[key] === "control_off" || statusData[key] === "data_collection_off" || statusData[key] === "Glucose") {
            setStatus(offMessage);
            clearTimeout(statusTimeout.current);
        }
    }, [statusData, key, onMessage, offMessage, shouldTimeout]);

    return (
        <div className={`status-box`} style={{ color: status.includes("ON") ? 'green' : 'red' }}>
            {status}
        </div>
    );
};

export default useStatusBox;