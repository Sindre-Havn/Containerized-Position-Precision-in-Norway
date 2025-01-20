
import { Html } from '@react-three/drei';
import React from 'react';



export const colors = {
  G: '#32CD32',  
  R: '#FFD700',  
  E: '#1E90FF',  
  C: '#FF1493',  
  J: '#4B0082',  
  I: '#FF8C00',  
  S: '#FF6347',  
};


export const Satellite = ({ position, label }) => (
    <mesh position={position}>
      <circleGeometry args={[0.1, 64]} />
      <meshBasicMaterial color={colors[label[0]]} />
      <Html distanceFactor={5}>
        <div style={{ color: 'black', background: 'white', padding: '2px' ,fontSize:'25px'}}>{label}</div>
      </Html>
    </mesh>
);

// Component for the interpolated satellite route


export const SatelliteMovement = ({ position, label }) => (
  <mesh position={position}>
    <circleGeometry args={[0.07, 32]} />
    <meshBasicMaterial color={colors[label[0]]} />
  </mesh>
);