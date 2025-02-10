import React from 'react';
import NavBar from './components/NavBar';
import FilterComponent from './components/Filtering';
import Visualization from './components/Visualization';
import NavMap from './components/MapComponent.js';
import { useAtom } from 'jotai';
import {updateDataState} from './states/states';
import './css/filtering.css';

function App() {
    const [updateData,setUpdateData] = useAtom(updateDataState);
    const handleUpdateData = () => {
        setUpdateData(true);
      }
    return (
        <div>
            <NavBar />
            <FilterComponent />
            <NavMap/>
            <div>
                <button className={`searchButton ${updateData ? 'loading' : ''}`} onClick={handleUpdateData} disabled={updateData}>{updateData ? '' : 'Search Satellites'}</button>
            </div>
            <Visualization />
  
        </div>
    );
}

export default App;