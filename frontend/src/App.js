import React from 'react';
import NavBar from './components/NavBar';
import FilterComponent from './components/Filtering';
import Visualization from './components/Visualization';


function App() {

    return (
        <div>
            <NavBar />
            <FilterComponent />
            <Visualization />
  
        </div>
    );
}

export default App;