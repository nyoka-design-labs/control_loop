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
        if (data[key] === "1" || data[key] === "3" || data[key] === "11" || data[key] === "13" || data[key] === "5" || data[key] === "7" || data[key] === "control_on" || data[key] === "data_collection_on" || data[key] === "Lactose" || data[key] === "15") {
          clearTimeout(statusTimeout.current);
          setStatus(onMessage);
          if (shouldTimeout) {
            statusTimeout.current = setTimeout(() => {
              setStatus(offMessage);
            }, 20000); // timeout
          }
        } else if (data[key] === "0" || data[key] === "2" || data[key] === "10" || data[key] === "12" || data[key] === "4" || data[key] === "6" || data[key] === "control_off" || data[key] === "data_collection_off" || data[key] === "Glucose" || data[key] === "14") {
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

// import React, { useState, useEffect, useRef } from 'react';
// import { useData } from '../DataContext';
// import '../App.css';

// const useStatusBox = (key, onMessage, offMessage, shouldTimeout = false) => {
//   const [status, setStatus] = useState(offMessage);
//   const { websocket } = useData();
//   const statusTimeout = useRef();
//   const statusConfigRef = useRef({});

//   useEffect(() => {
//     // Fetch the status configuration from the JSON file
//     fetch('/Users/mba_sam/Github/Nyoka Design Labs/control_loop/webapp/frontend/src/components/status_config.json')
//       .then(response => response.json())
//       .then(data => {
//         statusConfigRef.current = data; // Update the ref with the latest data
//         console.log("status config", statusConfigRef.current);
//       })
//       .catch(error => {
//         console.error('Error fetching status config:', error);
//       });
//   }, []);

//   useEffect(() => {
//     const handleMessage = (event) => {
//       const data = JSON.parse(event.data);
//       console.log("status", data);
//       console.log("status config", statusConfigRef.current); // Use the ref here
//       if (data.type === 'status' && statusConfigRef.current[key]) {
//         const [offStatus, onStatus] = statusConfigRef.current[key];
//         console.log("on status", onStatus);
//         console.log("off status", offStatus);
//         if (data[key] === onStatus) {
//           clearTimeout(statusTimeout.current);
//           setStatus(onMessage);
//           if (shouldTimeout) {
//             statusTimeout.current = setTimeout(() => {
//               setStatus(offMessage);
//             }, 20000); // timeout
//           }
//         } else if (data[key] === offStatus) {
//           setStatus(offMessage);
//           clearTimeout(statusTimeout.current);
//         }
//       }
//     };

//     if (websocket) {
//       websocket.addEventListener('message', handleMessage);
//     }

//     return () => {
//       if (websocket) {
//         websocket.removeEventListener('message', handleMessage);
//       }
//       clearTimeout(statusTimeout.current);
//     };
//   }, [websocket, key, onMessage, offMessage, shouldTimeout]); // Removed statusConfig from dependencies

//   return (
//     <div className={`status-box`} style={{ color: status.includes("ON") ? 'green' : 'red' }}>
//       {status}
//     </div>
//   );
// };

// export const useFeedPumpStatus = () => useStatusBox("feed_pump_status", "ON", "OFF");
// export const useBasePumpStatus = () => useStatusBox("base_pump_status", "ON", "OFF");
// export const useLactosePumpStatus = () => useStatusBox("lactose_pump_status", "ON", "OFF");
// export const useBufferPumpStatus = () => useStatusBox("buffer_pump_status", "ON", "OFF");
// export const useLysatePumpStatus = () => useStatusBox("lysate_pump_status", "ON", "OFF");
// export const useAcidPumpStatus = () => useStatusBox("acid_pump_status", "ON", "OFF");
// export const useControlLoopStatus = () => useStatusBox("control_loop_status", "ON", "OFF", true);
// export const useDataCollectionStatus = () => useStatusBox("data_collection_status", "ON", "OFF", true);
// export const useFeedMediaStatus = () => useStatusBox("feed_media", "Lactose Feed", "Glucose Feed");
