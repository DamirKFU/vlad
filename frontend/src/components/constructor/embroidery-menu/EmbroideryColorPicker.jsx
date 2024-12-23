import React from 'react';

const EmbroideryColorPicker = ({ stitchingOptions, selectedColors, onSelectColor }) => {
  return (
    <div className="container-field mb-6 flex flex-row items-center gap-4">
      <div className="container-field header-text w-48 text-2xl font-bold mb-2">ЦВЕТ ВЫШИВКИ</div>
      <div className="flex gap-4">
        {stitchingOptions.map((color) => (
          <div
            key={color}
            className="flex flex-col items-center gap-1"
            onClick={() => onSelectColor("art_color", color)}
          >
            <div
              className={`color-circle bg-${color} ${selectedColors.art_color === color ? "selected" : ""}`}
            />
            <span className="text-sm">{color}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmbroideryColorPicker; 