import React, { useState, useEffect, useRef } from 'react';
import { useData } from '../DataContext';
import mqtt from 'mqtt';
import '../App.css';

const useStatusBox = (key, onMessage, offMessage, shouldTimeout = false) => {
  const [status, setStatus] = useState(offMessage);
  const { websocket } = useData();
  const statusTimeout = useRef();

  useEffect(() => {
    const client = mqtt.connect('ws://192.168.0.25:9001');

    const handleMqttMessage = (topic, message) => {
      const data = JSON.parse(message.toString());
      if (data[key] === "1" || data[key] === "3" || data[key] === "5" || data[key] === "7" || data[key] === "9" || data[key] === "11" || data[key] === "13" || data[key] === "15" || data[key] === "control_on" || data[key] === "data_collection_on" || data[key] === "Lactose") {
        clearTimeout(statusTimeout.current);
        setStatus(onMessage);
        if (shouldTimeout) {
          statusTimeout.current = setTimeout(() => {
            setStatus(offMessage);
          }, 20000); // timeout
        }
      } else if (data[key] === "0" || data[key] === "2" || data[key] === "4" || data[key] === "6" || data[key] === "8" || data[key] === "10" || data[key] === "12" || data[key] === "14" || data[key] === "control_off" || data[key] === "data_collection_off" || data[key] === "Glucose") {
        setStatus(offMessage);
        clearTimeout(statusTimeout.current);
      }
    };

    client.on('connect', () => {
      console.log('Connected to MQTT broker');
      client.subscribe('status');
    });

    client.on('message', (topic, message) => {
      if (topic === 'status') {
        handleMqttMessage(topic, message);
      }
    });

    client.on('error', (error) => {
      console.error("MQTT error:", error);
    });

    return () => {
      console.log("Closing MQTT connection");
      client.end();
      clearTimeout(statusTimeout.current);
    };
  }, [key, onMessage, offMessage, shouldTimeout]);

  return (
    <div className={`status-box`} style={{ color: status.includes("ON") ? 'green' : 'red' }}>
      {status}
    </div>
  );
};

export default useStatusBox;