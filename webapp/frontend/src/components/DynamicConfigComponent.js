import React, { useState, useEffect } from 'react';
import { useData } from '../DataContext';

const DynamicConfigComponent = ({ loopIdentifier }) => {
    const { configData, websocket } = useData();
    const [config, setConfig] = useState(configData[loopIdentifier] || {});

    useEffect(() => {
        setConfig(configData[loopIdentifier] || {});
    }, [configData, loopIdentifier]);

    const handleChange = (key, value) => {
        setConfig({ ...config, [key]: value });
    };

    const handleSubmit = (key) => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({
                type: "update_config",
                loop_id: loopIdentifier,
                key: key,
                value: config[key]
            }));
        }
    };

    return (
        <div>
            {Object.keys(config).map((key) => (
                <div key={key} className="config-item">
                    <label>{key}:</label>
                    <input
                        type="text"
                        value={config[key]}
                        onChange={(e) => handleChange(key, e.target.value)}
                    />
                    <button onClick={() => handleSubmit(key)}>Update</button>
                </div>
            ))}
        </div>
    );
};

export default DynamicConfigComponent;