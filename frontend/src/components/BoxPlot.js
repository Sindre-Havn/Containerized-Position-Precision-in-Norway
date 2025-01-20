import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2'; // Use 'Bar' instead of 'BoxPlot'
import '../css/boxplot.css';

// Register the components needed for the Bar Chart
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export const BarChartGraph = ({ data, labels }) => {
  const numberList = data.map((array) => 
    array.reduce((totalLength, objects) => totalLength + objects.satellitesData.length, 0)
  );
  
  const barChartData = {
    labels: labels, // X-axis categories
    datasets: [
      {
        label: 'Number of Satellites in View',
        backgroundColor: 'rgba(255, 99, 132, 0.5)', // Bar color
        borderColor: 'rgba(255, 99, 132, 1)', // Bar border color
        borderWidth: 1,
        data: numberList, // Y-axis values
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      x: {
        beginAtZero: true,
      },
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
  <div className="bar-chart-container">
    <h4>Number of Satellites in View</h4>
    <Bar data={barChartData} options={options} /> 
  </div>
  );
};


