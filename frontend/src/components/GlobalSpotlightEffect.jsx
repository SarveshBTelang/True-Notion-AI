import React, { useState, useEffect, useRef } from 'react';
import './GlobalSpotlightEffect.css';

const GlobalSpotlightEffect = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseEnter = () => {
    setOpacity(1.);
  };

  const handleMouseLeave = () => {
    setOpacity(0);
  };

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseenter', handleMouseEnter);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div
      className="global-spotlight-effect"
      style={{
        opacity: opacity,
        background: `radial-gradient(3000px circle at ${position.x}px ${position.y}px, rgba(98, 108, 255, 0.2), transparent 40%)`,
      }}
    />
  );
};

export default GlobalSpotlightEffect;
