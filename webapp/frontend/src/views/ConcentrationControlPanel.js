import React from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import useStatusBox from '../components/StatusBoxes';
import DynamicComponents from '../components/DynamicComponents';
import DynamicConfigComponent from '../components/DynamicConfigComponent';
import { Graph } from '../components/Graph'; // Use the new Graph component
import './views.css';
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
        <div className="view-container">
            <h1>Concentration Control Panel</h1>
            <div className="view-content">
                <div className="graphs-section">
                    
                    <div className="mb-3">
                        <div className="button-status-container">
                            {dataCollectionButton}
                            {dataCollectionStatus}
                            {controlLoopButton}
                            {controlLoopStatus}
                        </div>
                    </div>
                    <div className="content">
                        <div className="graph-section">
                            <Tabs defaultActiveKey="buffer_weight" className="mb-3 custom-tabs">
                                <Tab eventKey="buffer_weight" title="Buffer Weight">
                                    <h3>Buffer Weight: {currentMeasurements.buffer_weight} g</h3>
                                    <Graph systemData={systemData} label="buffer_weight" actualColor="rgb(75, 192, 192)"
                                        expectedDataKey="buffer_weight" expectedColor="rgb(255, 99, 132)" />
                                </Tab>
                                <Tab eventKey="lysate_weight" title="Lysate Weight">
                                    <h3>Lysate Weight: {currentMeasurements.lysate_weight} g</h3>
                                    <Graph systemData={systemData} label="lysate_weight" actualColor="rgb(75, 192, 192)"
                                        expectedDataKey="lysate_weight" expectedColor="rgb(75, 192, 192)" />
                                </Tab>
                            </Tabs>
                        </div>
                    </div>
                </div>
                <div className="controls-section">
                    <div className="config-panel-dark">
                        <div className="right-aligned-buttons">
                            <div className="mb-3">
                                <DynamicComponents pumps={currentPumps} loopIdentifier={concentrationLoopIdentifier} />
                            </div>
                            <div className="config-section">
                                <DynamicConfigComponent loopIdentifier={concentrationLoopIdentifier} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConcentrationControlPanel;