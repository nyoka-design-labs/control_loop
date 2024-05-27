import React, { useState, useEffect, useRef } from 'react';
import { useData } from '../DataContext';
import '../App.css';

const useStatusBox = (key, onMessage, offMessage, shouldTimeout = false) => {
  const [status, setStatus] = useState(offMessage);
  const { websocket } = useData();
  const statusTimeout = useRef();

  useEffect(() => {
    const handleMessage = (event) => {
      const data = JSON.parse(event.data);
      // console.log(data)
      if (data.type === 'status') {
        if (data[key] === "1" || data[key] === "3" || data[key] === "11" || data[key] === "13" || data[key] === "5" || data[key] === "7" || data[key] === "control_on" || data[key] === "data_collection_on" || data[key] === "Lactose") {
          clearTimeout(statusTimeout.current);
          setStatus(onMessage);
          if (shouldTimeout) {
            statusTimeout.current = setTimeout(() => {
              setStatus(offMessage);
            }, 20000); // timeout
          }
        } else if (data[key] === "0" || data[key] === "2" || data[key] === "10" || data[key] === "12" || data[key] === "4" || data[key] === "6" || data[key] === "control_off" || data[key] === "data_collection_off" || data[key] === "Glucose") {
          setStatus(offMessage);
          clearTimeout(statusTimeout.current);
        }
      }
    };

    if (websocket) {
      websocket.addEventListener('message', handleMessage);
    }

    return () => {
      if (websocket) {
        websocket.removeEventListener('message', handleMessage);
      }
      clearTimeout(statusTimeout.current);
    };
  }, [websocket, key, onMessage, offMessage, shouldTimeout]); // Added all dependencies to useEffect to adhere to linting rules

  return (
    <div className={`status-box`} style={{ color: status.includes("ON") ? 'green' : 'red' }}>
      {status}
    </div>
  );
};

export const useFeedPumpStatus = () => useStatusBox("feed_pump_status", "ON", "OFF");
export const useBasePumpStatus = () => useStatusBox("base_pump_status", "ON", "OFF");
export const useLactosePumpStatus = () => useStatusBox("lactose_pump_status", "ON", "OFF");
export const useBufferPumpStatus = () => useStatusBox("buffer_pump_status", "ON", "OFF");
export const useLysatePumpStatus = () => useStatusBox("lysate_pump_status", "ON", "OFF");
export const useAcidPumpStatus = () => useStatusBox("acid_pump_status", "ON", "OFF");
export const useControlLoopStatus = () => useStatusBox("control_loop_status", "ON", "OFF", true);
export const useDataCollectionStatus = () => useStatusBox("data_collection_status", "ON", "OFF", true);
export const useFeedMediaStatus = () => useStatusBox("feed_media", "Lactose Feed", "Glucose Feed");

