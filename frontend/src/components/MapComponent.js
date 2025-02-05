import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-geosearch/dist/geosearch.css';
import { OpenStreetMapProvider, GeoSearchControl } from 'leaflet-geosearch';
import L from 'leaflet';
import customMarkerIcon from '../assets/pngwing.png';
import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import {endPointsState} from '../states/states';

// Fix Leaflet's default marker icon issue
const customIcon = new L.Icon({
    iconUrl: customMarkerIcon,
    iconSize: [32, 32], // Adjust size as needed
    iconAnchor: [16, 32], // Center the icon
    popupAnchor: [0, -32], // Adjust popup position
  });

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

const ClickableMap = ({ markers, setMarkers }) => {
  const [endPoints, setEndPoints ] = useAtom(endPointsState);
  useMapEvents({
    click(e) {
      if (markers.length < 2) {
        setMarkers([...markers, e.latlng]);
        setEndPoints()
      }
    },
  });

  return null;
};

const NavMap = () => {
  const [markers, setMarkers] = useState([]);

  // Function to remove a marker when clicked
  const handleMarkerClick = (index) => {
    setMarkers(markers.filter((_, i) => i !== index));
  };

  return (
    <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '10px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ClickableMap markers={markers} setMarkers={setMarkers} />
      {markers.map((position, index) => (
        <Marker key={index} position={position} icon={customIcon} eventHandlers={{ click: () => handleMarkerClick(index) }}>
          <Popup>Click to remove</Popup>
        </Marker>
      ))}
      <SearchControl />
    </MapContainer>
  );
};

export default NavMap;
