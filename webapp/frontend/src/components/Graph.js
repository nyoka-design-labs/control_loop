// Graph.js
import React from 'react';
import CanvasJSReact from './canvasjs.react'; // Make sure the path is correct
const CanvasJSChart = CanvasJSReact.CanvasJSChart;

export const Graph = ({ systemData, label, actualColor, expectedDataKey = null, expectedColor = 'rgb(255, 99, 132)' }) => {
    const dataPoints = systemData.map(data => ({ x: data.time, y: data[label.toLowerCase()] }));
    const expectedDataPoints = expectedDataKey ? systemData.map(data => ({ x: data.time, y: data[expectedDataKey.toLowerCase()] })) : [];

    const options = {
        theme: "light",
        animationEnabled: true,
        zoomEnabled: true,
        height: 650, // Set the height of the chart
        title: {
            text: ""
        },
        axisX: {
            interval: 1,
        },
        axisY: {
            title: '',
            includeZero: false
        },
        data: [
            {
                type: "line",
                name: `${label} Actual`,
                showInLegend: true,
                yValueFormatString: "#,##0.##",
                dataPoints: dataPoints,
                lineColor: actualColor
            },
            ...(expectedDataKey ? [{
                type: "line",
                name: `${expectedDataKey}`,
                showInLegend: true,
                yValueFormatString: "#,##0.##",
                dataPoints: expectedDataPoints,
                lineColor: expectedColor
            }] : [])
        ]
    };

    return (
        <div className="graph-container">
            <CanvasJSChart options={options} containerProps={{ height: "100%" }} />
        </div>
    );
};