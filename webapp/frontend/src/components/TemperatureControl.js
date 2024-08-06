// src/components/TemperatureControl.js

import React from 'react';
import TogglePumpButton from './TogglePumpButton'; // Import the toggle button component
import TempControlStatusBox from './TempControlStatusBox'; // Import the temperature control status box
import { useData } from '../DataContext'; // Import the useData hook

const TemperatureControl = ({ loopIdentifier }) => {
    const { statusData } = useData();
    const controlStatus = statusData['control_loop_status'] === 'control_on';

    return (
        <div className="button-status-container-dark">
            <TogglePumpButton 
                buttonLabel="Toggle Temp Control" 
                sendCommand="toggle_temp" 
                loopIdentifier={loopIdentifier} 
                disabled={!controlStatus}
            />
            <TempControlStatusBox statusKey="temp_control_status" offMessage="OFF" />
        </div>
    );
};

export default TemperatureControl;