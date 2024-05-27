import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

export const createChartData = (systemData, label, actualColor, expectedLabel, expectedColor) => {
    const currentDataPoints = label === 'Temperature'
      ? systemData.map(data => parseFloat(data.temp))
      : systemData.map(data => data[label.toLowerCase()]);
    // console.log("Charts system Data:", systemData);
    // console.log("Charts Current data points:", currentDataPoints);
    // console.log(currentDataPoints);
    const datasets = [
      {
        label: `${label} Actual`,
        data: currentDataPoints,
        borderColor: actualColor,
        fill: false,
        tension: 0.1
      }
    ];
  
    if (expectedLabel) {
      const expectedDataPoints = expectedLabel === 'Temperature'
      ? systemData.map(data => parseFloat(data.temp))
      : systemData.map(data => data[expectedLabel.toLowerCase()]);
      // console.log("Charts expected Data Points:", expectedDataPoints);
      // console.log("Charts expected label:", expectedLabel);
      // console.log("Charts system data label:", systemData);
      datasets.push({
        label: `${expectedLabel}`,
        data: expectedDataPoints,
        borderColor: expectedColor,
        fill: false,
        tension: 0.1  // Dashed line for expected data
      });
    }
  
    return {
      labels: systemData.map(data => data.time),
      datasets: datasets,
    };
  };

export const chartOptions = {
  plugins: {
    legend: {
      display: false
    }
  }
};

// A functional component to render a chart
export const Chart = ({ systemData, label, actualColor, expectedDataKey = null, expectedColor = 'rgb(255, 99, 132)' }) => {
    // console.log("Rendering Chart with systemData:", systemData);
    const data = createChartData(systemData, label, actualColor, expectedDataKey, expectedColor);
    return <Line data={data} options={chartOptions} />;
  };