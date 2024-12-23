import React from 'react';

const FontSelector = ({ fonts, selectedArtFont, handleArtFontChange }) => {
  return (
    <div className="container-field mb-6 w-full flex space-between items-center gap-4">
      <div className="container-field header-text w-48 text-2xl font-bold mb-2">ШРИФТ</div>
      {fonts.map((font) => (
        <div
          key={font}
          className={`item-size min-w-40 h-10 text-2xl text-center ${
            selectedArtFont.art_font === font ? "selected" : ""
          }`}
          onClick={() => handleArtFontChange("art_font", font)}
        >
          {font}
        </div>
      ))}
    </div>
  );
};

export default FontSelector; 