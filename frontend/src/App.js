import React from 'react';
import NavBar from './components/NavBar';
import FilterComponent from './components/Filtering';
import Visualization from './components/Visualization';
import NavMap from './components/MapComponent.js';
import { useAtom } from 'jotai';
import {updateDataState, chosenPointState} from './states/states';
import './css/filtering.css';

import { DOPLineChart } from './components/DOPplot.js';

function App() {

    const [updateData,setUpdateData] = useAtom(updateDataState);
    const [selectedPointIndex, setSelectedPointIndex] = useAtom(chosenPointState);

    const handleUpdateData = (selectedPointIndex) => {
        setUpdateData(true);
        setSelectedPointIndex(selectedPointIndex);
      }

    return (
        <div>
            <NavBar />
            <FilterComponent />
            <NavMap/>

            <DOPLineChart/>

            <div className="searchButtonContainer">                
                <button
                    className={`searchButton ${updateData ? 'loading' : ''}`}
                    onClick={() => handleUpdateData(selectedPointIndex)} // Sender inn punktnummer
                    disabled={updateData}
                >
                    {updateData ? '' : 'Search Satellites at Point Nr:'}
                </button>
                <input
                    type="number"
                    placeholder="Type in point nr..."
                    value={selectedPointIndex}
                    onChange={(e) => setSelectedPointIndex(e.target.value)}
                    className="point-input"
                />
            </div>

            <Visualization />
  
        </div>
    );
}

export default App;