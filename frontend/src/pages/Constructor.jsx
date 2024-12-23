import React, { useState } from "react";
import "../styles/Constructor.css";
import api from '../api';
import useCategories from '../hooks/useCategories';
import useImagePreview from '../hooks/useImagePreview';
import useConstructorState from '../hooks/useConstructorState';
import ItemMenu from '../components/constructor/item-menu/ItemMenu';
import EmbroideryMenu from '../components/constructor/embroidery-menu/EmbroideryMenu';
import { ITEM_TYPES, MENU_TABS } from '../constants/constructor';
import Preloader from '../components/common/Preloader';
import ErrorMessage from '../components/common/ErrorMessage';

const Constructor = () => {
  const { categories, isLoading, error } = useCategories();
  const { selectedImage, previewUrl, handleImageChange } = useImagePreview();
  const {
    imageUrl,
    selectedMenu,
    selectedItem,
    selectedColors,
    selectedItemSize,
    fadeClass,
    selectedArt,
    setSelectedMenu,
    setSelectedItem,
    setSelectedColors,
    setItemSize,
    setSelectedArt,
    changeImage
  } = useConstructorState(ITEM_TYPES);

  const [textareaValue, setTextareaValue] = useState('');
  const [displayText, setDisplayText] = useState('Вышиварт');
  const [selectedArtSize, setSelectedArtSize] = useState(null);
  const [selectedArtFont, setSelectedArtFont] = useState({
    art_font: "стандартный"
  });

  const categoryNames = categories.map((category) => category.category);
  const categoryItems = categories.map((category) => category.items);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    
    const itemId = categories[selectedItem % 4] 
      ? categories[selectedItem % 4].items.find(item => item.size === selectedItemSize.item_size)
          ?.details.find(detail => detail.color === selectedColors.product)?.id 
      : "no";
    
    formData.append('item_id', itemId);
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    const file = new File([blob], 'product-image.png', { type: 'image/png' });
    formData.append('image', file);

    if (selectedImage) {
      formData.append('embroidery_image', selectedImage, selectedImage.name);
    }

    try {
      const response = await api.post('catalog/constructor-product/create/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Success:', response);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleMenuClick = (menu) => setSelectedMenu(menu);

  const handleItemChange = (index) => {
    setSelectedItem(index);
    changeImage(ITEM_TYPES[index % ITEM_TYPES.length].colors["gray-800"][selectedArt.is_art]);
    const availableSizes = categoryItems[index]?.map(item => item.size) || [];
    const firstSize = availableSizes[0];
    
    const availableColors = categoryItems[index] 
      ? categoryItems[index].find(item => item.size === firstSize)?.details.map(detail => detail.color) || []
      : [];
    const firstColor = availableColors[0];

    setItemSize({ item_size: firstSize });
    setSelectedColors(prev => ({ ...prev, product: firstColor }));
  };

  const handleColorSelect = (type, color) => {
    setSelectedColors(prev => ({ ...prev, [type]: color }));
  };

  const handleItemSizeSelect = (type, size) => {
    const availableColors = categoryItems[selectedItem] 
      ? categoryItems[selectedItem].find(item => item.size === size)?.details.map(detail => detail.color) || []
      : [];
    const firstColor = availableColors[0];
    setItemSize(prev => ({ ...prev, [type]: size }));
    setSelectedColors(prev => ({ ...prev, product: firstColor }));
  };

  const handleTextareaChange = (value) => {
    setTextareaValue(value);
    setDisplayText(value.trim() === '' ? 'Вышиварт' : value);
  };

  const handleArtSizeChange = (event) => {
    setSelectedArtSize(event.target.value);
  };

  const handleArtFontChange = (type, font) => {
    setSelectedArtFont(prev => ({ ...prev, [type]: font }));
  };

  const handleArtSelect = (type, art) => {
    setSelectedArt(prev => ({ ...prev, [type]: art }));
    changeImage(ITEM_TYPES[selectedItem % ITEM_TYPES.length].colors["gray-800"][art]);
  };

  const isRadioSelected = (value) => selectedArtSize === value;

  if (isLoading) {
    return <Preloader message="Загрузка конструктора..." />;
  }

  if (error) {
    return <ErrorMessage 
      message={error} 
      onRetry={() => window.location.reload()}
    />;
  }

  return (
    <div className="constructor-container p-16">
      <div className="grid grid-cols-1 lg:grid-cols-5">
        <div className="col-span-3 relative">
          <img
            src={imageUrl}
            alt="Футболка"
            className={`transition-opacity duration-300 ${fadeClass}`}
          />
          <div className="text-overlay">
            <h1 className="overlay-text">{displayText}</h1>
          </div>
        </div>

        <div className="max-w-full col-span-2">
          <h1 className="header-text text-5xl font-bold mb-4">
            {categoryNames[selectedItem] || "sample text"}
          </h1>

          <div className="mb-6 flex">
            <button
              className={`menu-header ${selectedMenu === MENU_TABS.ITEM ? "active" : ""} font-bold text-xl w-full`}
              onClick={() => handleMenuClick(MENU_TABS.ITEM)}
            >
              ИЗДЕЛИЕ
            </button>
            <button
              className={`menu-header ${selectedMenu === MENU_TABS.EMBROIDERY ? "active" : ""} font-bold text-xl w-full`}
              onClick={() => handleMenuClick(MENU_TABS.EMBROIDERY)}
            >
              ВЫШИВКА
            </button>
          </div>

          {selectedMenu === MENU_TABS.ITEM ? (
            <ItemMenu
              selectedItem={selectedItem}
              handleItemChange={handleItemChange}
              selectedColors={selectedColors}
              onSelectColor={handleColorSelect}
              selectedItemSize={selectedItemSize}
              handleItemSizeSelect={handleItemSizeSelect}
              handleMenuClick={handleMenuClick}
              categoryNames={categoryNames}
              categoryItems={categoryItems}
            />
          ) : (
            <EmbroideryMenu
              textareaValue={textareaValue}
              handleTextareaChange={handleTextareaChange}
              isRadioSelected={isRadioSelected}
              handleArtSizeChange={handleArtSizeChange}
              selectedColors={selectedColors}
              onSelectColor={handleColorSelect}
              handleMenuClick={handleMenuClick}
              selectedArtFont={selectedArtFont}
              handleArtFontChange={handleArtFontChange}
              selectedArt={selectedArt}
              handleArtSelect={handleArtSelect}
              handleImageChange={handleImageChange}
              previewUrl={previewUrl}
              handleSubmit={handleSubmit}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Constructor;