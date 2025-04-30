
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
        <div style={{
          color: '#333',
          background: '#f5f5f5',
          padding: '2px 4px',             // litt bedre padding
          borderRadius: '8px',
          fontSize: '24px',               // gjort bittelitt mindre for bedre balanse
          fontWeight: 500,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'inline-block',
          border: `2px solid ${colors[label[0]]}`, // <-- her bruker vi border riktig
        }}>
          {label}
        </div>
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