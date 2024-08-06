// src/components/TempControlStatusBox.js

import React, { useState, useEffect, useRef } from 'react';
import { useData } from '../DataContext';
import '../App.css';

const TempControlStatusBox = ({ statusKey, offMessage }) => {
    const [status, setStatus] = useState(offMessage);
    const { statusData } = useData();
    const statusTimeout = useRef();

    useEffect(() => {
        console.log("Status Data:", statusData); // Debug log to see the statusData
        console.log("Status Key:", statusKey); // Debug log to see the statusKey
        if (statusData[statusKey] === "heating") {
            clearTimeout(statusTimeout.current);
            setStatus("HEATING");
        } else if (statusData[statusKey] === "cooling") {
            clearTimeout(statusTimeout.current);
            setStatus("COOLING");
        } else {
            setStatus(offMessage);
            clearTimeout(statusTimeout.current);
        }
    }, [statusData, statusKey, offMessage]);

    return (
        <div className={`status-box`} style={{ color: status === "HEATING" ? 'red' : status === "COOLING" ? 'blue' : 'grey' }}>
            {status}
        </div>
    );
};

export default TempControlStatusBox;