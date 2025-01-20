import axios from 'axios';
import React, { useState, useEffect } from 'react';

const PollingComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to check for the data
  const pollData = () => {
    axios.get('http://127.0.0.1:5000/satellites')
      .then(response => {
        if (response.data && response.data.data) {
          setData(response.data.data);  // Store the data when it is available
          setLoading(false);  // Stop loading once data is available
        }
      })
      .catch(error => {
        setError('Error fetching data');
        setLoading(false);
      });
  };

  // Polling using useEffect
  useEffect(() => {
    const intervalId = setInterval(pollData, 3000);  // Poll every 3 seconds

    // Cleanup function to stop polling when component unmounts
    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return <p>Loading data...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h2>Data Received</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default PollingComponent;
