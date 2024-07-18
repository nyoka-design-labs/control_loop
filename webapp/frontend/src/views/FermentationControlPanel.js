import React, { useState } from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import useStatusBox from '../components/StatusBoxes';
import DynamicComponents from '../components/DynamicComponents';
import DynamicConfigComponent from '../components/DynamicConfigComponent';
import { Graph } from '../components/Graph'; // Use the new Graph component
import './views.css';
import 'bootstrap/dist/css/bootstrap.min.css';

const FermentationControlPanel = () => {
    const { systemData, currentMeasurements, pumpData } = useData();
    const fermentationLoopIdentifier = 'fermentation_loop';

    const currentPumps = pumpData[fermentationLoopIdentifier] || {};

    const [controlLoopButton, isControlLoopRunning] = useControlLoopButton("start_control", "stop_control", fermentationLoopIdentifier);
    const dataCollectionButton = useDataCollectionButton("start_collection", "stop_collection", fermentationLoopIdentifier, isControlLoopRunning);
    const dataCollectionStatus = useStatusBox("data_collection_status", "ON", "OFF", true);
    const controlLoopStatus = useStatusBox("control_loop_status", "ON", "OFF", true);

    // State to force a re-render of the graph
    const [graphKey, setGraphKey] = useState(0);

    return (
        <div className="view-container">
            <h1>Fermentation Control Panel</h1>
            <div className="view-content">
                <div className="graphs-section">
                    <div className="content">
                        <div className="graph-section">
                            <Tabs
                                defaultActiveKey="weight"
                                className="mb-3 custom-tabs"
                                onSelect={() => setGraphKey(graphKey + 1)}
                            >
                                <Tab eventKey="weight" title="Weight">
                                    <h3>Feed Weight: {currentMeasurements.weight} g</h3>
                                    <Graph graphInstanceKey={graphKey} systemData={systemData} label="Feed_Weight" actualColor="rgb(75, 192, 192)" />
                                </Tab>
                                <Tab eventKey="do" title="DO">
                                    <h3>DO: {currentMeasurements.do} %</h3>
                                    <Graph graphInstanceKey={graphKey} systemData={systemData} label="do" actualColor="rgb(75, 192, 192)" />
                                </Tab>
                                <Tab eventKey="temp" title="Temperature">
                                    <h3>Temp: {currentMeasurements.temp} °C</h3>
                                    <Graph graphInstanceKey={graphKey} systemData={systemData} label="Temp" actualColor="rgb(75, 192, 192)" />
                                </Tab>
                                <Tab eventKey="ph" title="pH">
                                    <h3>pH: {currentMeasurements.ph}</h3>
                                    <Graph graphInstanceKey={graphKey} systemData={systemData} label="PH" actualColor="rgb(75, 192, 192)" />
                                </Tab>
                            </Tabs>
                        </div> 
                    </div>
                </div>
                <div className="controls-section">
                    <div className="mb-3">
                        <div className="button-status-container">
                            {dataCollectionButton}
                            {dataCollectionStatus}
                        </div>
                        <div className="button-status-container">
                            {controlLoopButton}
                            {controlLoopStatus}
                        </div>
                    </div>
                    <div className="config-panel-dark">
                        <div className="right-aligned-buttons">
                            <div className="mb-3">
                                <DynamicComponents pumps={currentPumps} loopIdentifier={fermentationLoopIdentifier} />
                            </div>
                            <div className="config-section">
                                <DynamicConfigComponent loopIdentifier={fermentationLoopIdentifier} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FermentationControlPanel;