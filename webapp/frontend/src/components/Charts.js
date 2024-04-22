import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

export const createChartData = (systemData, label, actualColor, expectedLabel, expectedColor) => {
    const currentDataPoints = label === 'Temperature'
      ? systemData.map(data => parseFloat(data.temp))
      : systemData.map(data => data[label.toLowerCase()]);
    
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
    const data = createChartData(systemData, label, actualColor, expectedDataKey, expectedColor);
    return <Line data={data} options={chartOptions} />;
  };