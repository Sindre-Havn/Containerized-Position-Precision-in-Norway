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
    const distance = useAtomValue(distanceState);
    const [updateDOP,setUpdateDOP] = useAtom(updateDOPState);
    //const [DOP, setDOP] = useState([]);
    const[GDOP,setGDOP] = useState([]);
    const[PDOP,setPDOP] = useState([]);
    const[TDOP,setTDOP] = useState([]);
    const[HDOP,setHDOP] = useState([]);
    const[VDOP,setVDOP] = useState([]);

    const [progress, setProgress] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    
    const labels = points.map((point) => point.properties.id);
    
    useEffect(() => {
        console.log('points :',points)
        if (!updateDOP) return; 

        // setIsProcessing(true);
        // setProgress(0);

        const filteredGNSS = Object.keys(gnssNames).filter((key) => gnssNames[key]);
        // if (eventSource) {
        //     eventSource.close();
        //   }
        // const dataSend = {
        //     time: time.toISOString(),
        //     elevationAngle: elevationAngle.toString(),
        //     GNSS: filteredGNSS,
        //     points: points,
        //     distance: distance.toString(),
        //   };
        
        //   // Send initial data to start processing
        //   fetch('http://localhost:5000/dopvalues', {
        //     method: 'POST',
        //     headers: {
        //       'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify(dataSend),
        //   }).catch(error => console.error('Error starting processing:', error));

        // // Create the EventSource
        // eventSource = new EventSource('http://localhost:5000/dopvalues');
        
        //   // Handle incoming messages
        // eventSource.onmessage = function(event) {
        //     const data = JSON.parse(event.data);
        //     if (data.progress) {
        //       // Update progress
        //       console.log(`Progress: ${data.progress}%`);
        //       setProgress(data.progress);
        //       // You can update a progress bar or other UI element here
        //     } else if (data.message && data.DOP) {
        //       // Final result
        
        //       console.log('DOP values:', data.DOP);
        //         setGDOP(data.DOP.map((array) => array[0]));
        //         setPDOP(data.DOP.map((array) => array[1]));
        //         setTDOP(data.DOP.map((array) => array[2]));
        //         setHDOP(data.DOP.map((array) => array[3]));
        //         setVDOP(data.DOP.map((array) => array[4]));
        //         setUpdateDOP(false);
        //       eventSource.close();
        //     }
        // };
        
        //   // Handle errors
        // eventSource.onerror = function(error) {
        //     console.error('EventSource failed:', error);
        //     eventSource.close();
        // };   


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
            distance: distance.toString(),
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
            console.log("updated", data);
            
            setGDOP(data.DOP.map((array) => array[0]));
            setPDOP(data.DOP.map((array) => array[1]));
            setTDOP(data.DOP.map((array) => array[2]));
            setHDOP(data.DOP.map((array) => array[3]));
            setVDOP(data.DOP.map((array) => array[4]));
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
        data: GDOP,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        pointBorderColor: 'rgba(75, 192, 192, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'PDOP',
        data: PDOP,
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        pointBorderColor: 'rgba(255, 99, 132, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'TDOP',
        data: TDOP,
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'HDOP',
        data: HDOP,
        borderColor: 'rgba(54, 162, 0, 1)',
        backgroundColor: 'rgba(54, 162, 0, 0.2)',
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      },
      {
        label: 'VDOP',
        data: VDOP,
        borderColor: 'rgba(54, 0, 235, 1)',
        backgroundColor: 'rgba(54, 0, 235, 0.2)',
        pointBorderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: '#fff',
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(220, 220, 220, 1)'
      }
    ]
  };

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

