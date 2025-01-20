import React, {useState} from 'react';
import { Canvas } from '@react-three/fiber';
import { Line, Text } from '@react-three/drei';
import { Satellite, colors } from './Satellite';
import { Vector3 } from 'three';
import '../css/skyplot.css';

function sphericalToCartesian2D(r, azimuth, zenith, center) {
  // Convert to radians
  azimuth = (azimuth * Math.PI) / 180 ;
  zenith = (zenith * Math.PI) / 180 ;

  // Calculate X and Y based on 2D plane
  const x = r * Math.sin(zenith) * Math.cos(azimuth) + center[0];
  const y = r * Math.sin(zenith) * Math.sin(azimuth) + center[1];

  
  const rotatedX = y; 
  const rotatedY = x; 

  return [rotatedX, rotatedY];
}

const SatelliteRoute = ({ points, color }) => (
  <Line
    points={points}  
    color={color}  // Line color
    lineWidth={2}  // Width of the line
    dashed={false}  // Optional: use dashed line if desired
  />
);
const CircleOutline = ({ radius, position, color, lineWidth, text }) => {
    const points = [];
    const textPoints = [];

    // Create points along the circumference of a circle
    for (let i = 0; i <= 100; i++) {
      const angle = (i / 100) * Math.PI * 2;
      points.push([Math.cos(angle) * radius, Math.sin(angle) * radius, 0]);
      textPoints.push([Math.cos(angle) * (radius*0.8), Math.sin(angle+45) * (radius*0.8), 0]);
    }

    return (
    <>
      <mesh
        position={position}
        rotation={[0, 0, 0]}
      >
        {/* Create the circular geometry */}
        <ringGeometry args={[radius - 0.05, radius, 64]} />
        <meshBasicMaterial color="white" side={1} />
      </mesh>
      <Line
        points={points} 
        color={color}
        lineWidth={lineWidth} 
        position={position}
        rotation={[0, 0, 0]} />
      <Text
        position={[textPoints[0][0],textPoints[0][1], textPoints[0][2]]} // Position of the Y-axis label
        fontSize={0.15}
        color="black"
      >
        {text}
      </Text>
    </>
    
  );
};
const Axes = ({ radius = 4.1, color = 'white', lineWidth = 2 }) => {
  // X-axis points
  const xAxisPoints = [
    [-radius, 0, 0], // From -radius to +radius on the X axis
    [radius, 0, 0],
  ];

  // Y-axis points
  const yAxisPoints = [
    [0, -radius, 0], // From -radius to +radius on the Y axis
    [0, radius, 0],
  ];

  return (
    <>
      {/* X-axis */}
      <Line
        points={xAxisPoints} // Array of [x, y, z] points
        color="grey" // X axis color
        lineWidth={lineWidth} // Optional: Adjust line thickness
      />
      <Text
        position={[radius + 0.25, 0, 0]} // Position of the X-axis label
        fontSize={0.2}
        color="black"
      >
        90°
      </Text>
      <Text
        position={[-radius - 0.3, 0, 0]} // Position of the X-axis label
        fontSize={0.2}
        color="black"
      >
        270°
      </Text>
      {/* Y-axis */}
      <Line
        points={yAxisPoints} // Array of [x, y, z] points
        color="grey" // Y axis color
        lineWidth={lineWidth} // Optional: Adjust line thickness
      />
      <Text
        position={[0, radius + 0.1, 0]} // Position of the Y-axis label
        fontSize={0.2}
        color="black"
      >
        0°
      </Text>
      <Text
        position={[0, -radius - 0.1, 0]} // Position of the Y-axis label
        fontSize={0.2}
        color="black"
      >
        180°
      </Text>
    </>
  );
};


export const SatelliteMap = ({satellites, cutOffElevation}) => {
  const center = [0, 0];
  const radius = 4;
  const cutOffRad = radius * Math.cos((cutOffElevation * Math.PI) / 180);
  const elevations = [0, 40, 70]; // Example: 0°, 40°, 70° elevations
  const radii = elevations.map(elev => radius * Math.cos((elev * Math.PI) / 180));
  let satellitesGrouped = {};
  // eslint-disable-next-line
  satellites.map((satellitesBefore, index) =>
    satellitesBefore.map((satellites, innerIndex) => {
      satellites.satellitesData.map((satellite) => {
        const color = colors[satellite.satName[0]];
        const { azimuth, zenith } = satellite;
        const coords = sphericalToCartesian2D(radius, azimuth, zenith, center);
        if (!satellitesGrouped[satellite.satName]) {
          satellitesGrouped[satellite.satName] = [[coords[0], coords[1], color]];
        }else{
          satellitesGrouped[satellite.satName].push([coords[0], coords[1], color]);
        }
      });
    }))
  //console.log(satellitesGrouped);
  return (
    <div className="skyplot-container">
      <Canvas className="skyplot-canvas" camera={{ position: [0, 0, 10], fov: 50 }}>
        <Axes/>
        <CircleOutline radius={cutOffRad} position={[0, 0, 0]} color={'black'}lineWidth={2} text = {cutOffElevation.toString() + '°' } />
        {radii.map((radius, index) => (
          <CircleOutline key={index} radius={radius} position={[0, 0, 0]} color={'grey'} lineWidth={1} text = {elevations[index] != 0? (elevations[index].toString() + '°') : ''} />
        ))}
        
        {Object.keys(satellitesGrouped).map((satName) => {
          let color = "white"
          const routePoints = satellitesGrouped[satName].map((satellite) => {
            color = satellite[2]
            return new Vector3(satellite[0], satellite[1], 0);
          })

          return (
            <SatelliteRoute
              key={`2`}
              points={routePoints}
              color={color}
            />
          );
        })}
      {Object.keys(satellitesGrouped).map((satName) => {
          const sattelittes = satellitesGrouped[satName];
          const sat = sattelittes[sattelittes.length - 1];
          return <Satellite key={sat[0]} position={[sat[0], sat[1], 0]} label={satName} />;
        })}
      </Canvas>
    </div>
  );
};

