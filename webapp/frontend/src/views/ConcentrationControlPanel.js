import React from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import useStatusBox from '../components/StatusBoxes';
import DynamicComponents from '../components/DynamicComponents';
import DynamicConfigComponent from '../components/DynamicConfigComponent';
import { Chart } from '../components/Charts';
import '../App.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const ConcentrationControlPanel = () => {
    const { systemData, currentMeasurements, pumpData } = useData();
    const concentrationLoopIdentifier = 'concentration_loop';

    const currentPumps = pumpData[concentrationLoopIdentifier] || {};

    const [controlLoopButton, isControlLoopRunning] = useControlLoopButton("start_control", "stop_control", concentrationLoopIdentifier);
    const dataCollectionButton = useDataCollectionButton("start_collection", "stop_collection", concentrationLoopIdentifier, isControlLoopRunning);
    const dataCollectionStatus = useStatusBox("data_collection_status", "ON", "OFF", true);
    const controlLoopStatus = useStatusBox("control_loop_status", "ON", "OFF", true);

    return (
        <div className="App container mt-5">
            <h1>Concentration Control Panel</h1>
            <div className="mb-3">
                <div className="button-status-container">
                    {dataCollectionButton}
                    {dataCollectionStatus}
                    {controlLoopButton}
                    {controlLoopStatus}
                </div>
            </div>
            <Tabs defaultActiveKey="buffer_weight" className="mb-3">
                <Tab eventKey="buffer_weight" title="Buffer Weight">
                    <h3>Buffer Weight: {currentMeasurements.buffer_weight} g</h3>
                    <Chart systemData={systemData} label="buffer_weight" actualColor="rgb(75, 192, 192)"
                        expectedDataKey="buffer_weight" expectedColor="rgb(255, 99, 132)" />
                </Tab>
                <Tab eventKey="lysate_weight" title="Lysate Weight">
                    <h3>Lysate Weight: {currentMeasurements.lysate_weight} g</h3>
                    <Chart systemData={systemData} label="lysate_weight" color="rgb(75, 192, 192)"
                        expectedDataKey="lysate_weight" expectedColor="rgb(75, 192, 192)" />
                </Tab>
            </Tabs>

            <div className="control-panel">
                

                <div className="right-aligned-buttons">
                    <div className="mb-3">
                        <DynamicComponents pumps={currentPumps} loopIdentifier={concentrationLoopIdentifier} />
                    </div>
                    <div className="config-section">
\                        <DynamicConfigComponent loopIdentifier={concentrationLoopIdentifier} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConcentrationControlPanel;