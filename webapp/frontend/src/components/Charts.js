import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

export const createChartData = (systemData, label, color) => {
  const dataPoints = label === 'Temperature'
    ? systemData.map(data => parseFloat(data.temp))
    : systemData.map(data => data[label.toLowerCase()]);

  return {
    labels: systemData.map(data => data.time),
    datasets: [{
      label: `${label} Over Time`,
      data: dataPoints,
      borderColor: color,
      fill: false,
      tension: 0.1
    }],
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
export const Chart = ({ systemData, label, color }) => {
  const data = createChartData(systemData, label, color);
  return <Line data={data} options={chartOptions} />;
};
