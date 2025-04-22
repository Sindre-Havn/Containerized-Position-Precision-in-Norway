import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents,GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-geosearch/dist/geosearch.css';
import { OpenStreetMapProvider, GeoSearchControl } from 'leaflet-geosearch';
import L from 'leaflet';
import customMarkerIcon from '../assets/pngwing.png';
import A from '../assets/A.png';
import B from '../assets/B.png';
import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import {startPointState, endPointState, distanceState, roadState,pointsState, vegReferanseState} from '../states/states';
import '../css/map.css';
import proj4 from 'proj4';

// Define WGS84 (latitude/longitude) and UTM Zone 33 (Easting/Northing)
proj4.defs("EPSG:4326", "+proj=longlat +datum=WGS84 +no_defs");
proj4.defs("EPSG:32633", "+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs");



// Fix Leaflet's default marker icon issue
const customIcon = new L.Icon({
    iconUrl: customMarkerIcon,
    iconSize: [15, 15],
    iconAnchor: [8, 17],
    popupAnchor: [0, -32], 
  });
const endstopCustomIcon = new L.Icon({
    iconUrl: B,
    iconSize: [22, 30],   
    iconAnchor: [16, 32], 
    popupAnchor: [0, -32],
  });
const startstopCustomIcon = new L.Icon({
    iconUrl: A,
    iconSize: [22, 30],   
    iconAnchor: [16, 32], 
    popupAnchor: [0, -32],
  });


const position = [62.4280096, 	7.9440244]; // Example coordinates 

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

// funksjon for å kunne sette endestop markers
const ClickableMap = ({ setStartMarker, setEndMarker, startMarker, endMarker }) => {
  const setStartPoint = useSetAtom(startPointState);
  const setEndPoint = useSetAtom(endPointState);

  const convertToUTM = (latlng) => {
    const [easting, northing] = proj4("EPSG:4326", "EPSG:32633", [latlng.lng, latlng.lat]);
    return [easting, northing];
  };

  useMapEvents({
    click(e) {
      const { latlng } = e;

      // Hvis ingen startMarker: sett start
      if (!startMarker) {
        setStartMarker(latlng);
        setStartPoint(convertToUTM(latlng));
      }
      // Hvis start er satt men slutt ikke er det: sett slutt
      else if (!endMarker) {
        setEndMarker(latlng);
        setEndPoint(convertToUTM(latlng));
      }
    },
  });

  return null;
};

const NavMap = () => {
  const [vegreferanse, setVegsystemreferanse ]= useAtom(vegReferanseState);
  const [startPoint, setStartPoint] = useAtom(startPointState);
  const [endPoint, setEndPoint] = useAtom(endPointState);
  const distance = useAtomValue(distanceState);
  const [updateRoad,setUpdateRoad] = useAtom(roadState);
  const [markers, setMarkers] = useAtom(pointsState);
  const [geoJsonData, setGeoJsonData] = useState(null);
  
  const [startMarker, setStartMarker] = useState(null);
  const [endMarker, setEndMarker] = useState(null);

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
        vegReferanse: vegreferanse,
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
        console.log("road", data.road);
        console.log("points", data.points);
        setGeoJsonData(data.road);
        setMarkers(data.points);
        setUpdateRoad(false);
      })
      .catch(error => {
        console.error('Fetch error road:', error);
        console.error('Error name road:', error.name);
        console.error('Error message road:', error.message);
      });
  }, [geoJsonData, updateRoad, startPoint, endPoint, distance, setGeoJsonData, setUpdateRoad, vegreferanse, setMarkers]);
  
  useEffect(() => {
    fetchRoadData();
  }, [fetchRoadData]);

  const handleClearRoad = (e) => {
    setEndMarker(null);
    setStartMarker(null);
    setStartPoint([124657.85,	6957624.16]);
    setEndPoint([193510.27,6896504.01]);
    setMarkers([]);
    setVegsystemreferanse('EV136');
    setGeoJsonData(null);
  };

  return (
  <div className="map" >
    <MapContainer center={position} zoom={9} style={{ height: '400px', width: '100%', borderRadius: '10px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ClickableMap
        setStartMarker={setStartMarker}
        setEndMarker={setEndMarker}
        startMarker={startMarker}
        endMarker={endMarker}
      />
      {startMarker && (
        <Marker
          position={startMarker}
          icon={startstopCustomIcon}
          eventHandlers={{
            click: () => {
              setStartMarker(null);
              setStartPoint(null);
            }
          }}
        >
          <Popup>Klikk for å fjerne startpunkt</Popup>
        </Marker>
      )}

      {endMarker && (
        <Marker
          position={endMarker}
          icon={endstopCustomIcon}
          eventHandlers={{
            click: () => {
              setEndMarker(null);
              setEndPoint(null);
            }
          }}
        >
          <Popup>Klikk for å fjerne endepunkt</Popup>
        </Marker>
      )}

      <SearchControl />
      {geoJsonData && (geoJsonData.map((data, index) => (
        <GeoJSON
            key={index}
            data={data}
            style={{ color: 'black', weight: 5, opacity: 1 }}
          />
        ))
      )}
      {markers.length > 0 ?  (markers.map((point, index) => (
          <Marker key={index} position={[point.geometry.coordinates[1],point.geometry.coordinates[0] ]} icon={customIcon}>
            <Popup> Distance: {point.properties.distance_from_start}m</Popup>
          </Marker>
          ))
        ):null
      }
    </MapContainer>
    {markers.length > 0 ? 
      (<button className="clear-road-button" onClick={handleClearRoad}>
        Clear road
      </button>):null
    }
  </div>
  );
};

export default NavMap;
