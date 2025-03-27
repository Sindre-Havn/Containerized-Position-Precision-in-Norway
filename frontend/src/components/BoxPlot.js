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
        label: 'Satellites',
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
        labels: {
          font: {
            size: 14,           // 🔠 Størrelse på legend-tekst
            weight: 'bold'      // evt: 'normal', '500', etc.
          },
          color: '#003344'          // 🎨 Farge på legend-tekst
        }
      },
      title: {
        display: true,
        text: 'Number of Satellites in View',
        font: {
          size: 18,             // 🔠 Størrelse på tittel
          weight: 'bold'
        },
        color: '#222'           // 🎨 Tittelfarge
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Epoch Times',
          font: {
            size: 14
          },
          color: '#333'
        },
        ticks: {
          color: '#333',
          font: {
            size: 12
          }
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Satellites',
          font: {
            size: 14
          },
          color: '#333'
        },
        ticks: {
          color: '#333',
          font: {
            size: 12
          }
        }
      }
    }
  };

  return (
  <div className="bar-chart-container">
    <Bar data={barChartData} options={options} /> 
  </div>
  );
};


