import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import '../css/lineplot.css';
import { useAtom, useAtomValue } from 'jotai';
import { useState, useEffect } from 'react';
import { gnssState, elevationState, timeState, epochState, pointsState, updateDOPState } from '../states/states';
// Register the necessary components for line charts
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);



export const DOPLineChart = () => {
    // eslint-disable-next-line no-unused-vars  

    const gnssNames = useAtomValue(gnssState);
    const elevationAngle = useAtomValue(elevationState);
    const time =useAtomValue(timeState);
    const epoch = useAtomValue(epochState);
    const points = useAtomValue(pointsState);

    const [updateDOP,setUpdateDOP] = useAtom(updateDOPState);

    const[DOP,setDOP] = useState([]);


    const [progress, setProgress] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    
    const labels = points.map((point) => Math.round(point.properties.distance_from_start));
    useEffect(() => {
      if (!updateDOP) return;
      setIsProcessing(true);
  
      const filteredGNSS = Object.keys(gnssNames).filter((key) => gnssNames[key]);
  
      const payload = {
          time: time.toISOString(),
          elevationAngle: elevationAngle.toString(),
          epoch: epoch.toString(),
          GNSS: filteredGNSS,  // Already an array, no need to convert to string
          points: points       // Send directly as an array
      };
  
      fetch('http://127.0.0.1:5000/dopvalues', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
      })
      .then(response => {
          const reader = response.body.getReader();
          let dopData = [];
  
          const readStream = async () => {
              const decoder = new TextDecoder();
              while (true) {
                  const { done, value } = await reader.read();
                  if (done) break;
  
                  const text = decoder.decode(value);
                  console.log('Received text:', text);
                  if (text.startsWith('[')) {
                      try {
                          dopData = JSON.parse(text);
                          const array_of_arrays = dopData.map(arr => arr[0]);
                          setDOP(array_of_arrays);
                          setUpdateDOP(false);
                          setIsProcessing(false);
                      } catch (error) {
                          console.error('Error parsing DOP data:', error);
                      }
                  } else {
                      const uptprogress = parseInt(text, 10);
                      setProgress(uptprogress);
                      console.log(`Progress: ${uptprogress}%`);
                  }
              }
          };
  
          readStream();
      })
      .catch(error => {
          console.error('Error:', error);
      });
  }, [updateDOP, gnssNames, elevationAngle, time, epoch, points, setUpdateDOP]);

    
    const handleUpdateDOP = () => {
        setUpdateDOP(true);
      }
  // Instillinger for de ulike linjene i linjediagrammet
  const chartData = {
    labels: labels,
    datasets: [
      {
        label: 'GDOP',
        data: DOP.map((array) => array[0]),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        pointBorderColor: 'rgba(75, 192, 192, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'PDOP',
        data: DOP.map((array) => array[1]),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        pointBorderColor: 'rgba(255, 99, 132, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'TDOP',
        data: DOP.map((array) => array[2]),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'HDOP',
        data: DOP.map((array) => array[3]),
        borderColor: 'rgba(54, 162, 0, 1)',
        backgroundColor: 'rgba(54, 162, 0, 0.2)',
        pointBorderColor: 'rgba(54, 162, 0, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 0, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'VDOP',
        data: DOP.map((array) => array[4]),
        borderColor: 'rgba(54, 0, 235, 1)',
        backgroundColor: 'rgba(54, 0, 235, 0.2)',
        pointBorderColor: 'rgba(54, 0, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 0, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      }
    ]
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
        text: 'DOP Values Line Chart Along The road at Specified Points',
        font: {
          size: 18,            
          weight: 'bold'
        },
        color: '#222'          
      },
      tooltip: {
        backgroundColor: '#fff',
        titleColor: '#333',
        bodyColor: '#333',
        borderColor: '#ccc',
        borderWidth: 1,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          title: function (tooltipItems) {
            const index = tooltipItems[0].dataIndex;
            return `Point ${index}`;
          },
          label: function (tooltipItem) {
            const datasetLabel = tooltipItem.dataset.label || '';
            const value = tooltipItem.formattedValue;
            return `${datasetLabel}: ${value}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Distance in meters from the start',
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
          text: 'DOP Value',
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
    <div className="line-chart-container">
        <div>
            <button className={`searchButton ${updateDOP ? 'loading' : ''}`} onClick={handleUpdateDOP} disabled={updateDOP}>{updateDOP ? '' : 'Find DOP Line Chart'}</button>
        </div>
        {/* Loading Bar */}
        {isProcessing && (
            <div className='loadingbar'>
            <div className='progress'
              style={{width: `${progress}%`}}>
            </div>
            <div className='progress-text'>
              {progress}%
            </div>
            </div>
        )}
      {/* DOP line Chart Along Road */}
      <Line data={chartData} options={options} />
    </div>
  );
};

