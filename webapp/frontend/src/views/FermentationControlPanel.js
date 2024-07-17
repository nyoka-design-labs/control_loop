import React from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { useData } from '../DataContext';
import { useDataCollectionButton, useControlLoopButton } from '../components/Buttons';
import useStatusBox from '../components/StatusBoxes';
import DynamicComponents from '../components/DynamicComponents';
import DynamicConfigComponent from '../components/DynamicConfigComponent';
import { Chart } from '../components/Charts';
import './views.css';
import 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';

const FermentationControlPanel = () => {
    const { systemData, currentMeasurements, pumpData } = useData();
    const fermentationLoopIdentifier = 'fermentation_loop';

    const currentPumps = pumpData[fermentationLoopIdentifier] || {};

    const [controlLoopButton, isControlLoopRunning] = useControlLoopButton("start_control", "stop_control", fermentationLoopIdentifier);
    const dataCollectionButton = useDataCollectionButton("start_collection", "stop_collection", fermentationLoopIdentifier, isControlLoopRunning);
    const dataCollectionStatus = useStatusBox("data_collection_status", "ON", "OFF", true);
    const controlLoopStatus = useStatusBox("control_loop_status", "ON", "OFF", true);

    return (
        <div className="view-container">
            <h1>Fermentation Control Panel</h1>
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
                            <Tabs defaultActiveKey="weight" className="mb-3 custom-tabs">
                                <Tab eventKey="weight" title="Weight">
                                    <h3>Feed Weight: {currentMeasurements.weight} g</h3>
                                    <h3>Lactose Weight: {currentMeasurements.expected_weight} g</h3>
                                    <Chart systemData={systemData} label="Feed_Weight" actualColor="rgb(75, 192, 192)"
                                        expectedDataKey="lactose_weight" expectedColor="rgb(255, 99, 132)" />
                                </Tab>
                                <Tab eventKey="do" title="DO">
                                    <h3>DO: {currentMeasurements.do} %</h3>
                                    <Chart systemData={systemData} label="do" color="rgb(75, 192, 192)"
                                        expectedDataKey="do" expectedColor="rgb(75, 192, 192)" />
                                </Tab>
                                <Tab eventKey="temp" title="Temperature">
                                    <h3>Temp: {currentMeasurements.temp} °C</h3>
                                    <Chart systemData={systemData} label="Temperature" color="rgb(75, 192, 192)"
                                        expectedDataKey="Temperature" expectedColor="rgb(75, 192, 192)" />
                                </Tab>
                                <Tab eventKey="ph" title="pH">
                                    <div className="mb-3">
                                        <h3>pH: {currentMeasurements.ph}</h3>
                                    </div>
                                    <Chart systemData={systemData} label="PH" color="rgb(75, 192, 192)"
                                        expectedDataKey="PH" expectedColor="rgb(75, 192, 192)" />
                                </Tab>
                            </Tabs>
                        </div>
                        
                    </div>
                </div>
                <div className="controls-section">
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
