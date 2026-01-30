import React, { useState } from "react";
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
  require("../assets/mahal14.jpeg"),
  require("../assets/mahal15.jpeg"),
  require("../assets/mahal16.jpeg"),
];

const GalleryPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const openModal = (index) => {
    setCurrentIndex(index);
    setSelectedImage(galleryImages[index]);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const nextImage = () => {
    const newIndex = (currentIndex + 1) % galleryImages.length;
    setCurrentIndex(newIndex);
    setSelectedImage(galleryImages[newIndex]);
  };

  const prevImage = () => {
    const newIndex = (currentIndex - 1 + galleryImages.length) % galleryImages.length;
    setCurrentIndex(newIndex);
    setSelectedImage(galleryImages[newIndex]);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!selectedImage) return;
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'ArrowLeft') prevImage();
    if (e.key === 'Escape') closeModal();
  };

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedImage, currentIndex]);

  return (
    <div className="home-container">
      <div className="gallery-grid-container">
        <h2 className="gallery-grid-title">Our Gallery</h2>
        <p className="gallery-subtitle">Explore our beautiful venue through images</p>
        
        <div className="gallery-grid">
          {galleryImages.map((img, index) => (
            <div 
              className="gallery-grid-item" 
              key={index}
              onClick={() => openModal(index)}
            >
              <img src={img} alt={`Gallery ${index + 1}`} />
              <div className="gallery-overlay">
                <span className="gallery-overlay-text">View Image</span>
              </div>
            </div>
          ))}
        </div>

        {/* Modal/Lightbox */}
        {selectedImage && (
          <div className="gallery-modal" onClick={closeModal}>
            <span className="gallery-modal-close">&times;</span>
            
            <button className="gallery-modal-prev" onClick={(e) => { e.stopPropagation(); prevImage(); }}>
              &#10094;
            </button>
            
            <div className="gallery-modal-content" onClick={(e) => e.stopPropagation()}>
              <img src={selectedImage} alt="Full size" />
              <div className="gallery-modal-caption">
                Image {currentIndex + 1} of {galleryImages.length}
              </div>
            </div>
            
            <button className="gallery-modal-next" onClick={(e) => { e.stopPropagation(); nextImage(); }}>
              &#10095;
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GalleryPage;