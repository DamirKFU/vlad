import React from 'react';

const SizeSelector = ({ sizes, selectedItemSize, handleItemSizeSelect }) => {
  return (
    <div className="container-field mb-6 flex flex-row gap-4">
      <div className="container-field header-text w-48 text-2xl font-bold mb-2">РАЗМЕР</div>
      <div className="flex gap-4">
        {sizes.map((size) => (
          <div
            key={size}
            className={`item-size min-w-10 h-8 text-xl text-center ${
              selectedItemSize.item_size === size ? "selected" : ""
            }`}
            onClick={() => handleItemSizeSelect("item_size", size)}
          >
            {size}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SizeSelector; 