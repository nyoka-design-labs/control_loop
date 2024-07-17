import React, { useState } from 'react';
import { Button, Offcanvas } from 'react-bootstrap';
import FermentationControlPanel from './views/FermentationControlPanel';
import ConcentrationControlPanel from './views/ConcentrationControlPanel';
import Devices from './views/Devices';
import { DataProvider } from './DataContext';
import './App.css';

function App() {
    const [showOffcanvas, setShowOffcanvas] = useState(false);
    const [activeTab, setActiveTab] = useState('FermentationControl');

    const selectTab = (tabName) => {
        setActiveTab(tabName);
        setShowOffcanvas(false);
    };

    return (
        <DataProvider>
            <div className="full-page-container">
                <div className="menu-button-container">
                    <Button className="custom-menu-button" onClick={() => setShowOffcanvas(true)}>MENU</Button>
                </div>
                <Offcanvas show={showOffcanvas} onHide={() => setShowOffcanvas(false)} placement="start">
                    <Offcanvas.Header closeButton>
                        <Offcanvas.Title>MENU</Offcanvas.Title>
                    </Offcanvas.Header>
                    <Offcanvas.Body>
                        <div className="nav flex-column">
                            <Button variant="dark" onClick={() => selectTab('devices')}>Devices</Button>
                            <Button variant="dark" onClick={() => selectTab('FermentationControl')}>Fermentation Control Panel</Button>
                            <Button variant="dark" onClick={() => selectTab('ConcentrationControlPanel')}>Concentration Control Panel</Button>
                        </div>
                    </Offcanvas.Body>
                </Offcanvas>
                <div className="main-content mt-4">
                    {activeTab === 'FermentationControl' && <FermentationControlPanel />}
                    {activeTab === 'devices' && <Devices />}
                    {activeTab === 'ConcentrationControlPanel' && <ConcentrationControlPanel />}
                </div>
            </div>
        </DataProvider>
    );
}

export default App;