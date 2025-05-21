import React from 'react';
import { useAtom, useAtomValue } from 'jotai';
import {elevationState,timeState, gnssState, epochState, startPointState, endPointState, distanceState, roadState, vegReferanseState,geoJsonDataState, epochFrequencyState,roadProgressState} from '../states/states';
import '../css/filtering.css';
import { useState } from 'react';



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
  const [geoJsonData, setGeoJsonData] = useAtom(geoJsonDataState);
  const [epochFrequency, setEpochFrequency] = useAtom(epochFrequencyState);
  const progressRoad = useAtomValue(roadProgressState);

  const [startInput, setStartInput] = useState(startPoint);
  const [endInput, setEndInput] = useState(endPoint);
  const handleCheckboxChange = (e) => {
    setGnssNames({
      ...gnssNames,
      [e.target.name]: !gnssNames[e.target.name],
    });
  };

  const handleDateChange = (event) => {
    const localTime = event.target.value; 
    const utcTime = new Date(localTime + ":00.000Z"); // Append UTC format and create Date object
    setTime(utcTime); 
  };

  const handleElevationAngleChange = (e) => {
    setElevationAngle(e.target.value);
  };


  const handleUpdateRoad = () => {
    // setEndMarker(null);
    // setStartMarker(null);
    // setMarkers([]);
    setGeoJsonData(null);
    setUpdateRoad(true);
  }
  const handleHourChange = (event) => {
    setHours(event.target.value);
  };

  const handleSetStartPoint = (event) => {
    const input = event.target.value;
    setStartInput(input); // ← oppdater inputfeltet uansett
  
    if (input.trim() === "") {
      setStartPoint(null);
      return;
    }
  
    const coordinates = input.split(',').map(coord => parseFloat(coord.trim()));
    if (coordinates.length === 2 && coordinates.every(coord => !isNaN(coord))) {
      setStartPoint(coordinates);
    }
  };
  const handleSetEndPoint = (event) => {
    const input = event.target.value;
    setEndInput(input);
  
    if (input.trim() === "") {
      setEndPoint(null);
      return;
    }
  
    const coordinates = input.split(',').map(coord => parseFloat(coord.trim()));
    if (coordinates.length === 2 && coordinates.every(coord => !isNaN(coord))) {
      setEndPoint(coordinates);
    }
  };
  
  return (
    <>
    <div className="filter-header">
      <h2>Filter Options</h2>
    </div>
    <div className="filter-container">
      <div className="filter-comps">
        <div className="road-comps">
          <div>
            <h4 className="road-comps-header">Vegsystemreferanse</h4>
            <input
              type="text"
              value={vegsystemreferanse}
              onChange={(e) => setVegsystemreferanse(e.target.value)}
              placeholder="F.eks. EV136 ..."
              className='road-input1'
            />
            
          </div>

          <div>
            <h4 className="road-comps-header">Distance:</h4>
            <input
              type="number"
              value={distance}
              onChange={(e) => setDistance(e.target.value)}
              placeholder="Distance between measurings..."
              className='road-input2'
            />
          </div>

          <div>
            <h4 className="road-comps-header">Start Point (E,N)</h4>
            <input
              type="text"
              value={startInput}
              onChange={handleSetStartPoint}
              placeholder="Enter point E,N ..."
              className='road-input3'
            />
            
          </div>
          <div>
            <h4 className="road-comps-header">End Point (E,N)</h4>
            <input
              type="text"
              value={endInput}
              onChange={handleSetEndPoint}
              placeholder="Enter point E,N..."
              className='road-input3'
            />
          </div>
      
          <div className="road-button-container">
            <div className="button-wrapper">
              <button
                className={`searchButton ${updateRoad ? 'loading' : ''}`}
                onClick={handleUpdateRoad}
                disabled={updateRoad}
              >
                {updateRoad ? '' : 'Find Road'}
              </button>

              {updateRoad && (
                <p>Generating road ... {progressRoad}%</p>
              )}
            </div>
          </div>

        </div>
        
        <div className='satellite-comps'>
          <div className="checkbox-group">
            <h4 className="checkbox-title">GNSS Names</h4>
            <div className="checkbox-options">
              {Object.keys(gnssNames).map((name) => (
                <div className="checkbox-wrapper" key={name}>
                  <input className="inp-cbx" id={name} name={name} type="checkbox" checked={gnssNames[name]} onChange={handleCheckboxChange} />
                  <label className="cbx" htmlFor={name}>
                    <span>
                      <svg width="12px" height="10px" viewBox="0 0 12 10">
                        <polyline points="1.5 6 4.5 9 10.5 1"></polyline>
                      </svg>
                    </span>
                    <span>{name}</span>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="horizontal-group">
            <div>
              <h4>Time of Day (UTC)</h4>
              <input
                type="datetime-local"
                value={time.toISOString().slice(0, 16)}
                onChange={handleDateChange} />
            </div>
            <div className='elevation-angle'> 
              <div className='slider-header'>
                <p><b>Elevation Angle</b> {elevationAngle}°</p>
              </div>
              <input
                // className='elevation-angle-slider'
                className='uniform-slider'
                type="range"
                min="10"
                max="90"
                value={elevationAngle}
                onChange={handleElevationAngleChange} />
            </div>

          </div>
          <div className="horizontal-group2">
            <div className='epoch-angle'> 
              <div className='slider-header'>
                <p><b>Time Epoch</b> {hours} h</p>
              </div>
              <input
                className='uniform-slider'
                type="range"
                min="0"
                max="48"
                value={hours}
                onChange={handleHourChange} />
            </div>
            <div className='time-resolution'>
              <div className='slider-header'>
                <p><b>Calculation Interval</b> every {epochFrequency} min</p>
              </div>
              <input
                className='uniform-slider'
                type="range"
                min="10"
                max="60"
                step="10"
                value={epochFrequency}
                onChange={(e) => setEpochFrequency(parseInt(e.target.value))} />
            </div>
          </div>
        </div>
      </div>
    </div>
</>
  );
};

export default FilterComponent;