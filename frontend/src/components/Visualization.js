
import React, { useEffect, useState } from 'react';
import { useAtom, useAtomValue } from 'jotai'
import {elevationState, updateDataState,timeState, gnssState, epochState} from '../states/states';
import { SatelliteMap } from './SkyPlot';
import '../css/visualization.css';
import { BarChartGraph } from './BoxPlot';
import { LineChart } from './LinePlot';


const gps = {
  G: 'GPS',
  R: 'GLONASS',
  E: 'Galileo',
  C: 'BeiDou',
  J: 'QZSS',
  I: 'IRNSS',
  S: 'SBAS',
};
const colors = {
  G: '#32CD32',  
  R: '#FFD700',  
  E: '#1E90FF',  
  C: '#FF1493',  
  J: '#4B0082',  
  I: '#FF8C00',  
  S: '#FF6347',  
};



function fixData(data) {
  return data.map((satellites) => {
    const finalArray = [];
    satellites.forEach((satellite, index) => {
      const satNumbers = Object.keys(satellite.Satelitenumber);
      const label = satellite.Satelitenumber[satNumbers[0]];
      const typeLabel = gps[label[0]]
      const color = colors[label[0]];
      const satellitesData = [];
      
      satNumbers.forEach((key) => {
        const satName = satellite.Satelitenumber[key];
        const satCoord = [satellite.X[key], satellite.Y[key], satellite.Z[key]];
        const time = satellite.time[key];
        const azimuth = satellite.azimuth[key];
        const zenith = satellite.zenith[key];
        satellitesData.push({
          'satName': satName,
          'satCoord': satCoord,
          'time': time,
          'azimuth': azimuth,
          'zenith': zenith
        });
      });

      finalArray.push({
        'type': typeLabel,
        'color': color,
        'satellitesData': satellitesData
      });
    });

    return finalArray;
  });
}

// Main visualization component
const Visualization = () => {
    const [satellites,setSatellites] = useState([])
    // eslint-disable-next-line no-unused-vars  
    const [error, setError] = useState('')
    const [updateData,setUpdateData] = useAtom(updateDataState);
    const gnssNames = useAtomValue(gnssState);
    const elevationAngle = useAtomValue(elevationState);
    const time =useAtomValue(timeState);
    const epoch = useAtomValue(epochState);
    const labels = Array.from({ length: 2 * epoch +1}, (_, i) => 
      new Date(time.getTime() + i * 30 * 60 * 1000).toISOString().slice(11, 16)
    );
    const [DOP, setDOP] = useState([[0,0,0]]);

    useEffect(() => {
      //setLoading(true);
    
      const filteredGNSS = Object.keys(gnssNames).filter((key) => gnssNames[key]);
    
      fetch('http://127.0.0.1:5000/satellites', {
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
          setSatellites(fixData(data.data));
          setDOP(data.DOP);
          setUpdateData(false);
        })
        .catch(error => {
          console.error('Fetch error:', error);
          console.error('Error name:', error.name);
          console.error('Error message:', error.message);
        });
      


    }, [updateData]);
    
  if (updateData) {
    return <p>Loading data...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }
  return (
    !satellites || satellites.length === 0 ? (
      <p>Click on the update button to fetch data</p>
    ) : (
      <>
      {/* Skyplot and Table Row */}
      <div className="skyplot-table-container">
        {/* Skyplot Container */}
        <div className='skyplot'>
          <SatelliteMap satellites={satellites} cutOffElevation={elevationAngle} />
        </div>
      {/* Satellite Table */}
        <div className="satellite-table">
          {satellites[satellites.length - 1].map((satelliteGroup, index) => {
            const satType = satelliteGroup.type;
            const color = satelliteGroup.color;
            return (
              <div key={index} className="satellite-column">
                <div className="satellite-name" style={{ backgroundColor: color }}>
                  {satType}
                </div>
                {satelliteGroup.satellitesData.map((satellite, satIndex) => {
                  const satName = satellite.satName;
                  return (
                    <div key={satName} className="satellite-number">
                      <p>{satName}</p>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart Row: Bar Chart and Line Chart */}
      <div className="chart-row">
        {/* Bar Chart */}
        <div className="chart-container">
          <BarChartGraph data={satellites} labels={labels} />
        </div>

        {/* Line Chart */}
        <div className="chart-container">
          <LineChart data={DOP} labels={labels} satellites = {satellites} />
        </div>
      </div>
    </>
    )
  );
  
};

export default Visualization;
