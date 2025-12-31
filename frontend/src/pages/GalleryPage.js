import React, { useState, useEffect } from "react";
import "../App.css";

const galleryImages = [
  require("../assets/mahal1.webp"),
  require("../assets/mahal2.webp"),
  require("../assets/mahal3.webp"),
  require("../assets/mahal4.webp"),
  require("../assets/mahal5.webp"),
  require("../assets/mahal6.webp"),
  require("../assets/mahal7.webp"),
  require("../assets/mahal8.webp"),
  require("../assets/mahal9.webp"),
  require("../assets/mahal10.webp"),
  require("../assets/mahal11.webp"),
  require("../assets/mahal12.webp"),
  require("../assets/mahal13.webp"),
];

const GalleryPage = () => {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (paused) return;
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % galleryImages.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [paused]);

  return (
    <div className="home-container">
      <div className="gallery-container">
        <h2 className="gallery-title">Our Gallery</h2>
        <div
          className="gallery-slider"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
        >
          {galleryImages.map((img, i) => (
            <div
              className={`gallery-slide ${i === index ? "active" : ""}`}
              key={i}
            >
              <img src={img} alt={`gallery-${i}`} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GalleryPage;