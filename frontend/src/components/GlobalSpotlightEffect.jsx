import React, { useState, useEffect } from 'react';
import './GlobalSpotlightEffect.css';

const GlobalSpotlightEffect = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);
  const [radius, setRadius] = useState(3000); // default large radius

  // Update radius based on window width
  const updateRadius = () => {
    const width = window.innerWidth;

    if (width < 768) {
      setRadius(1200); // small screens
    } else if (width < 1200) {
      setRadius(2000); // medium screens
    } else {
      setRadius(3000); // large screens
    }
  };

  useEffect(() => {
    updateRadius(); // set initial radius
    window.addEventListener('resize', updateRadius);

    return () => {
      window.removeEventListener('resize', updateRadius);
    };
  }, []);

  const handleMouseMove = (e) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseEnter = () => {
    setOpacity(1);
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
        background: `radial-gradient(${radius}px circle at ${position.x}px ${position.y}px, rgba(98, 108, 255, 0.2), transparent 40%)`,
      }}
    />
  );
};

export default GlobalSpotlightEffect;
