import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2'; 
import '../css/boxplot.css';

// Register the components needed for the Bar Chart
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

// Barchart of numbers of satellites in view
export const BarChartGraph = ({ data, labels }) => {
  const numberList = data.map((array) => 
    array.reduce((totalLength, objects) => totalLength + objects.satellitesData.length, 0)
  );
  
  const barChartData = {
    labels: labels, 
    datasets: [
      {
        label: 'Satellites',
        backgroundColor: 'rgba(22, 34, 251, 0.5)', 
        borderColor: 'rgb(22, 34, 251)', 
        borderWidth: 1,
        data: numberList,
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
            size: 14,         
            weight: 'bold'    
          },
          color: '#003344'    
        }
      },
      title: {
        display: true,
        text: 'Number of Satellites in View',
        font: {
          size: 18,          
          weight: 'bold'
        },
        color: '#222'              
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


