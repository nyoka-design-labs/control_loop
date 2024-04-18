import React, { useState } from 'react';
import { Button, Offcanvas } from 'react-bootstrap';
import SystemControlPanel from './views/SystemControlPanel';
import Devices from './views/Devices';
import { DataProvider } from './DataContext';
import './App.css';

function App() {
    const [showOffcanvas, setShowOffcanvas] = useState(false);
    const [activeTab, setActiveTab] = useState('SystemControl');

    const selectTab = (tabName) => {
        setActiveTab(tabName);
        setShowOffcanvas(false);
    };

    return (
        <DataProvider>
            <div className="App container mt-5">
                <Button variant="primary" onClick={() => setShowOffcanvas(true)}>MENU</Button>
                <Offcanvas show={showOffcanvas} onHide={() => setShowOffcanvas(false)} placement="start">
                    <Offcanvas.Header closeButton>
                        <Offcanvas.Title>MENU</Offcanvas.Title>
                    </Offcanvas.Header>
                    <Offcanvas.Body>
                        <div className="nav flex-column">
                            <Button variant="dark" onClick={() => selectTab('SystemControl')}>System Control Panel</Button>
                            <Button variant="dark" onClick={() => selectTab('devices')}>Devices</Button>
                        </div>
                    </Offcanvas.Body>
                </Offcanvas>
                <div className="main-content mt-4">
                    {activeTab === 'SystemControl' && <SystemControlPanel />}
                    {activeTab === 'devices' && <Devices />}
                </div>
            </div>
        </DataProvider>
    );
}

export default App;
