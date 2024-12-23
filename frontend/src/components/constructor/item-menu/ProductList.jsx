import React from 'react';

const ProductList = ({ itemTypes, selectedItem, handleItemChange }) => {
  return (
    <div className="container-field mb-6 flex flex-row gap-4">
      <div className="container-field header-text w-48 text-2xl font-bold mb-2">ИЗДЕЛИЕ</div>
      <div className="product-options flex flex-col">
        {itemTypes.map((option, index) => (
          <label
            key={index}
            className={`product-option text-xl text-gray-400 mb-2 p-2 cursor-pointer rounded-md ${
              selectedItem === index ? 'border-2 border-black selected' : ''
            }`}
          >
            <input
              type="radio"
              name="product"
              checked={selectedItem === index}
              onChange={() => handleItemChange(index)}
              className="mr-2"
            />
            {option}
          </label>
        ))}
      </div>
    </div>
  );
};

export default ProductList; 