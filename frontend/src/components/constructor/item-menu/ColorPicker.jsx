import React from 'react';

const ColorPicker = ({ colorOptions, selectedColors, onSelectColor }) => {
  return (
    <div className="container-field mb-6 flex flex-row gap-4">
      <div className="container-field header-text w-48 text-2xl font-bold mb-2">ЦВЕТ ИЗДЕЛИЯ</div>
      <div className="flex gap-4">
        {colorOptions.map((color) => (
          <div
            key={color.color}
            className="flex flex-col items-center gap-1"
            onClick={() => onSelectColor("product", color.color)}
          >
            <div
              className={`color-circle ${selectedColors.product === color.color ? "selected" : ""}`}
              style={{ backgroundColor: color.hex }}
            />
            <span className="text-sm">{color.color}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ColorPicker; 