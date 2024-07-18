// Graph.js
import React from 'react';
import CanvasJSReact from './canvasjs.react'; // Make sure the path is correct
const CanvasJSChart = CanvasJSReact.CanvasJSChart;

export const Graph = ({ systemData, label, actualColor, expectedDataKey = null, expectedColor = 'rgb(255, 99, 132)', key }) => {
    const dataPoints = systemData.map(data => ({ x: data.time, y: data[label.toLowerCase()] }));
    const expectedDataPoints = expectedDataKey ? systemData.map(data => ({ x: data.time, y: data[expectedDataKey.toLowerCase()] })) : [];

    const options = {
        theme: "light",
        animationEnabled: false,
        zoomEnabled: true,
        height: 650,
        title: {
            text: ""
        },
        axisX: {
            title: "",
            valueFormatString: "#,##0.####", // Format to show the float values\
        },
        axisY: {
            title: '',
            includeZero: false
        },
        data: [
            {
                type: "line",
                name: `${label}`,
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
            <CanvasJSChart key={key} options={options} />
        </div>
    );
};