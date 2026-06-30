import React, { useEffect, useState } from "react";
import "./BeatLoader.css";

const BeatLoader = ({ color, size }) => {
  const [dotCount, setDotCount] = useState(3); // Number of bouncing dots
  const delay = 170; // Delay between each dot animation

  useEffect(() => {
    const interval = setInterval(() => {
      setDotCount((prevDotCount) => (prevDotCount + 1) % 4);
    }, delay);

    return () => clearInterval(interval);
  }, []);

  const dots = Array.from({ length: 3 }, (_, index) => (
    <div
      key={index}
      className={`dot ${index === dotCount ? "active" : ""}`}
      style={{ backgroundColor: color || "#096DD9", width: size || 7, height: size || 7 }}
      data-testid="dots"
    />
  ));

  return <div className="beat-loader" data-testid="beat-loader-id">{dots}</div>;
};

export default BeatLoader;
