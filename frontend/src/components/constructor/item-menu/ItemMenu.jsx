import React from 'react';
import ProductList from './ProductList';
import SizeSelector from './SizeSelector';
import ColorPicker from './ColorPicker';

const Menu1 = ({ 
  selectedItem, 
  handleItemChange, 
  selectedColors, 
  onSelectColor, 
  selectedItemSize, 
  handleItemSizeSelect, 
  handleMenuClick, 
  categoryNames, 
  categoryItems 
}) => {
  const colorOptions = categoryItems[selectedItem] 
    ? categoryItems[selectedItem].find(item => item.size === selectedItemSize.item_size)?.details.map(detail => ({ 
        color: detail.color, 
        hex: detail.hex 
      })) || [] 
    : [];
  const itemTypes = categoryNames;
  const sizes = categoryItems[selectedItem]?.map(item => item.size) || [];

  return (
    <>
      <ProductList 
        itemTypes={itemTypes}
        selectedItem={selectedItem}
        handleItemChange={handleItemChange}
      />

      <SizeSelector 
        sizes={sizes}
        selectedItemSize={selectedItemSize}
        handleItemSizeSelect={handleItemSizeSelect}
      />

      <ColorPicker 
        colorOptions={colorOptions}
        selectedColors={selectedColors}
        onSelectColor={onSelectColor}
      />

      <hr className="border-t border-gray-300 my-4" />
      <div className="flex justify-end">
        <button 
          className="bg-gray-800 text-white px-6 py-2 rounded font-bold" 
          onClick={() => handleMenuClick(2)}
        >
          ВЫШИВКА →
        </button>
      </div>
    </>
  );
};

export default Menu1; 