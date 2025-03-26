import React from 'react';
import { useAtom } from 'jotai';
import {elevationState, updateDataState,timeState, gnssState, epochState, startPointState, endPointState, distanceState, roadState, vegReferanseState} from '../states/states';
import '../css/filtering.css';


const FilterComponent = () => {
  const [gnssNames, setGnssNames] = useAtom(gnssState);
  const [elevationAngle, setElevationAngle] = useAtom(elevationState)
  const [time, setTime] =useAtom(timeState);
  const [hours, setHours] = useAtom(epochState);
  
  const [vegsystemreferanse, setVegsystemreferanse] = useAtom(vegReferanseState);
  const [startPoint, setStartPoint] = useAtom(startPointState);
  const [endPoint, setEndPoint] = useAtom(endPointState);
  const [distance, setDistance] = useAtom(distanceState);
  const [updateRoad,setUpdateRoad] = useAtom(roadState);

  const handleCheckboxChange = (e) => {
    setGnssNames({
      ...gnssNames,
      [e.target.name]: e.target.checked,
    });
  };

  const handleDateChange = (event) => {
    const localTime = event.target.value; // Get the selected local time string
    const utcTime = new Date(localTime + ":00.000Z"); // Append UTC format and create Date object
    setTime(utcTime); // Update state with UTC date
  };

  const handleElevationAngleChange = (e) => {
    setElevationAngle(e.target.value);
  };


  const handleUpdateRoad = () => {
    setUpdateRoad(true);
  }
  const handleHourChange = (event) => {
    setHours(event.target.value);
  };
  return (
    <>
    <div className="filter-header">
      <h2>Filter Options</h2>
    </div>
    <div className="filter-container">
      
      <div className="filter-comps">
        <div className="checkbox-group">
          <h4>GNSS Names</h4>
          {Object.keys(gnssNames).map((name) => (
            <label key={name}>
              <input
                type="checkbox"
                name={name}
                checked={gnssNames[name]}
                onChange={handleCheckboxChange} />
              {name}
            </label>
          ))}
        </div>
        <div className="horizontal-group">
          <div>
            <h4>Time of Day (UTC)</h4>
            <input
              type="datetime-local"
              value={time.toISOString().slice(0, 16)}
              onChange={handleDateChange} />
          </div>
          <div>
            <div className='slider-header'>
              <h4>Time Epoch</h4>
              <span>{hours} h</span>
            </div>
            <input
              type="range"
              min="0"
              max="48"
              value={hours}
              onChange={handleHourChange} />

          </div>
        </div>
        <div>
          <div className='slider-header'>
            <h4>Elevation Angle</h4>
            <p>{elevationAngle}°</p>
          </div>
          <input
            className='elevation-angle'
            type="range"
            min="10"
            max="90"
            value={elevationAngle}
            onChange={handleElevationAngleChange} />
        </div>
      </div>
      <div className="road-comps">
        {/* New Inputs */}
        <div>
          <h4>Vegsystemreferanse</h4>
          <input
            type="text"
            value={vegsystemreferanse}
            onChange={(e) => setVegsystemreferanse(e.target.value)}
            placeholder="F.eks. EV136 ..."
          />
          
        </div>
        <div>
          <h4>Start Point E,N</h4>
          <input
            type="text"
            value={startPoint}
            onChange={(e) => setStartPoint(e.target.value)}
            placeholder="Enter point E,N ..."
          />
          
        </div>
        <div>
          <h4>End Point E,N</h4>
          <input
            type="text"
            value={endPoint}
            onChange={(e) => setEndPoint(e.target.value)}
            placeholder="Enter point E,N..."
          />
        </div>
    
        <div>
          <h4>Distance between measurings</h4>
          <input
            type="number"
            value={distance}
            onChange={(e) => setDistance(e.target.value)}
            placeholder="Enter distance..."
          />
        </div>

        <button className={`searchButton ${updateRoad ? 'loading' : ''}`} onClick={handleUpdateRoad} disabled={updateRoad}>{updateRoad ? '' : 'Find Road'}</button>
      </div>
      {/* <NavMap /> */}
    </div>
</>
  );
};

export default FilterComponent;