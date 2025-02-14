import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents,GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-geosearch/dist/geosearch.css';
import { OpenStreetMapProvider, GeoSearchControl } from 'leaflet-geosearch';
import L from 'leaflet';
import customMarkerIcon from '../assets/pngwing.png';
import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import {startPointState, endPointState, distanceState, roadState} from '../states/states';
import '../css/map.css';


// Fix Leaflet's default marker icon issue
const customIcon = new L.Icon({
    iconUrl: customMarkerIcon,
    iconSize: [32, 32], // Adjust size as needed
    iconAnchor: [16, 32], // Center the icon
    popupAnchor: [0, -32], // Adjust popup position
  });
const colors = [
    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFF2",
    "#F2FF33", "#FF8C33", "#33FFA1", "#A1FF33", "#8C33FF", "#FF336E",
    "#33A1FF", "#FFD633", "#33FFD6", "#FF33F2", "#F233FF", "#FF5733",
    "#5733FF", "#D633FF", "#33FF8C", "#FFA133", "#33D6FF", "#F2A133",
    "#8CFF33", "#336EFF"
  ];
const position = [62.47714, 7.772829]; // Example coordinates

const SearchControl = () => {
  const map = useMap();

  useEffect(() => {
    const provider = new OpenStreetMapProvider();
    const searchControl = new GeoSearchControl({
      provider,
      style: 'bar',
      showMarker: true,
      showPopup: false,
      marker: { color: 'red' },
      retainZoomLevel: false,
      animateZoom: true,
      autoClose: true,
      searchLabel: 'Enter address',
    });

    map.addControl(searchControl);
    return () => map.removeControl(searchControl);
  }, [map]);

  return null;
};


// const ClickableMap = ({ markers, setMarkers }) => {
//   const [endPoints, setEndPoints ] = useAtom(endPointsState);

//   useMapEvents({
//     click(e) {
//       if (markers.length < 2) {
//         setMarkers([...markers, e.latlng]);
//         setEndPoints([...endPoints, e.latlng]);
//       }
//     },
//   });

//   return null;
// };

const NavMap = () => {
  const startPoint = useAtomValue(startPointState);
  const endPoint = useAtomValue(endPointState);
  const distance = useAtomValue(distanceState);
  const [updateRoad,setUpdateRoad] = useAtom(roadState);
  const [markers, setMarkers] = useState([]);
  const [geoJsonData, setGeoJsonData] = useState(null);
  

  const fetchRoadData = useCallback(() => {
    if (geoJsonData != null || !updateRoad) return;
  
    console.log("startPoint", startPoint);
    console.log("endPoint", endPoint);
  
    fetch('http://127.0.0.1:5000/road', {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      method: 'POST',
      body: JSON.stringify({
        startPoint: startPoint,
        endPoint: endPoint,
        distance: distance,
      }),
      mode: 'cors',
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log("road", data.data);
        setGeoJsonData(data.data);
        setUpdateRoad(false);
      })
      .catch(error => {
        console.error('Fetch error road:', error);
        console.error('Error name road:', error.name);
        console.error('Error message road:', error.message);
      });
  }, [geoJsonData, updateRoad, startPoint, endPoint, distance, setGeoJsonData, setUpdateRoad]);
  
  useEffect(() => {
    fetchRoadData();
  }, [fetchRoadData]);
  // Function to remove a marker when clicked
  const handleMarkerClick = (index) => {
    setMarkers(markers.filter((_, i) => i !== index));
  };

  return (
  <div className="map" >
    <MapContainer center={position} zoom={13} style={{ height: '80vh', width: '100%', borderRadius: '10px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {/* <ClickableMap markers={markers} setMarkers={setMarkers} /> */}
      {/* {markers.map((position, index) => (
        <Marker key={index} position={position} icon={customIcon} eventHandlers={{ click: () => handleMarkerClick(index) }}>
          <Popup>Click to remove</Popup>
        </Marker>
      ))} */}
      <SearchControl />
      {/* {geoJsonData && (geoJsonData.map((data, index) => (
        <GeoJSON
            key={index}
            data={data}
            style={{ color: colors[index], weight: 5, opacity: 1 }} // Tilpass farge & sti
          />
        ))
      )} */}
      {geoJsonData && 
        <GeoJSON
            key={145}
            data={geoJsonData}
            style={{ color: "black", weight: 5, opacity: 1 }} // Tilpass farge & sti
          />
        
      }
    </MapContainer>
  </div>
  );
};

export default NavMap;
