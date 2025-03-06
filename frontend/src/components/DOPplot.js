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
import { gnssState, elevationState, timeState, epochState, pointsState, distanceState, updateDOPState } from '../states/states';
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


    // time = data.get('time').strip('Z')
    // elevation_angle = data.get('elevationAngle')
    // gnss = data.get('GNSS')
    // points = data.get('points')
    // distance = data.get('distance')
    // eslint-disable-next-line no-unused-vars  

    const gnssNames = useAtomValue(gnssState);
    const elevationAngle = useAtomValue(elevationState);
    const time =useAtomValue(timeState);
    const epoch = useAtomValue(epochState);
    const points = useAtomValue(pointsState);

    const [updateDOP,setUpdateDOP] = useAtom(updateDOPState);
    //const [DOP, setDOP] = useState([]);
    const[DOP,setDOP] = useState([]);


    const [progress, setProgress] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    
    const labels = points.map((point) => Math.round(point.properties.distance_from_start));
    
    useEffect(() => {
        console.log('points :',points)
        if (!updateDOP) return; 

        const filteredGNSS = Object.keys(gnssNames).filter((key) => gnssNames[key]);

        fetch('http://127.0.0.1:5000/dopvalues', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        method: 'POST',
        body: JSON.stringify({
            time: time.toISOString(),
            elevationAngle: elevationAngle.toString(),
            epoch: epoch.toString(),
            GNSS: filteredGNSS,
            points: points,
        }),
        mode: 'cors'
        })
        .then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json(); 
        })
        .then(data => {
            console.log("updated dop", data.DOP.map(arr => arr[0]));
            const array_of_arrays = data.DOP.map(arr => arr[0]);
            setDOP(array_of_arrays);
            setUpdateDOP(false);
        })
        .catch(error => {
            console.error('Fetch error:', error);
            console.error('Error name:', error.name);
            console.error('Error message:', error.message);
        });
        


     }, [updateDOP]);
    
    const handleUpdateDOP = () => {
        setUpdateDOP(true);
      }
  // Single chart configuration with multiple datasets
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
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'VDOP',
        data: DOP.map((array) => array[4]),
        borderColor: 'rgba(54, 0, 235, 1)',
        backgroundColor: 'rgba(54, 0, 235, 0.2)',
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      }
    ]
  };
  console.log(chartData);
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: 'DOP Values'
      }
    },
    scales: {
      y: {
        beginAtZero: true
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
            <div style={{ width: '100%', backgroundColor: '#ddd', marginBottom: '10px' }}>
            <div
                style={{
                width: `${progress}%`,
                height: '10px',
                backgroundColor: 'green',
                transition: 'width 0.3s ease-in-out',
                }}
            ></div>
            </div>
        )}
      <h4>DOP Values Line Chart Along The road at Specified Points</h4>
      <Line data={chartData} options={options} /> {/* Use the 'Line' component here */}
    </div>
  );
};

