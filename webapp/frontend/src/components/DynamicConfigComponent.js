import React, { useState, useEffect } from 'react';
import { useData } from '../DataContext';
import './components.css';

const DynamicConfigComponent = ({ loopIdentifier }) => {
    const { configData } = useData();
    const [config, setConfig] = useState(configData[loopIdentifier] || {});

    useEffect(() => {
        setConfig(configData[loopIdentifier] || {});
    }, [configData, loopIdentifier]);

    const handleChange = (key, value) => {
        setConfig({ ...config, [key]: value });
    };

    const handleSubmit = async (key) => {
        try {
            const response = await fetch('/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    loop_id: loopIdentifier,
                    key: key,
                    value: config[key]
                })
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const responseData = await response.json();
            console.log('Config update response:', responseData);
        } catch (error) {
            console.error('Error updating config:', error);
        }
    };

    return (
        <div className="config-panel-dark">
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