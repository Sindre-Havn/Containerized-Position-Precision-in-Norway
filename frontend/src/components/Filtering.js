import React from 'react';
import { useAtom } from 'jotai';
import {elevationState, updateDataState,timeState, gnssState, epochState} from '../states/states';
import '../css/filtering.css';

const FilterComponent = () => {
  const [gnssNames, setGnssNames] = useAtom(gnssState);
  const [elevationAngle, setElevationAngle] = useAtom(elevationState)
  const [time, setTime] =useAtom(timeState);
  const [hours, setHours] = useAtom(epochState);
  const [updateData,setUpdateData] = useAtom(updateDataState)

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

  const handleUpdateData = () => {
    setUpdateData(true);
  }
  const handleHourChange = (event) => {
    setHours(event.target.value);
  };


  return (
    <div className="filter-container">
      <h3>Filter Options</h3>

      <div className="checkbox-group">
        <h4>GNSS Names</h4>
        {Object.keys(gnssNames).map((name) => (
          <label key={name}>
            <input
              type="checkbox"
              name={name}
              checked={gnssNames[name]}
              onChange={handleCheckboxChange}
            />
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
            onChange={handleDateChange}
          />
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
            onChange={handleHourChange}
          />
          
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
          onChange={handleElevationAngleChange}
        />
      </div>
      <div>
        <button className={`searchButton ${updateData ? 'loading' : ''}`} onClick={handleUpdateData} disabled={updateData}>{updateData ? '' : 'Search Satellites'}</button>
      </div>
    </div>
  );
};

export default FilterComponent;