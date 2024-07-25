import React from 'react';
import { Button } from 'react-bootstrap';

const TogglePumpButton = ({ buttonLabel, sendCommand, loopIdentifier }) => {
  const handleToggle = async () => {
    try {
      const response = await fetch('/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: sendCommand,
          loopID: loopIdentifier,
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Pump toggled:', data);
    } catch (error) {
      console.error('Error toggling pump:', error);
    }
  };

  return (
    <Button variant="secondary" onClick={handleToggle} className="me-2">
      {buttonLabel}
    </Button>
  );
};

export default TogglePumpButton;