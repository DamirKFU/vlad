import React, { useState } from 'react';
import TextInput from './TextInput';
import SizeRadio from './SizeRadio';
import EmbroideryColorPicker from './EmbroideryColorPicker';
import FontSelector from './FontSelector';
import ImageUpload from './ImageUpload';

const Menu2 = ({ 
  textareaValue, 
  handleTextareaChange: handleTextareaChangeProp,
  isRadioSelected, 
  handleArtSizeChange, 
  selectedColors, 
  onSelectColor, 
  handleMenuClick, 
  selectedArtFont, 
  handleArtFontChange, 
  selectedArt, 
  handleArtSelect,
  handleImageChange,
  previewUrl,
  handleSubmit
}) => {
  const [error, setError] = useState('');
  const [displayText, setDisplayText] = useState('Вышиварт');

  const options = ["0.8 - 1", "1.3 - 1.5"];
  const stitchingOptions = ["gray-800", "green-300", "pink-300"];
  const fonts = ["стандартный", "рукописный"];
  const arts = ["убрать", "добавить"];

  const handleTextareaChange = (value) => {
    console.log('Textarea value:', value);
    handleTextareaChangeProp(value);

    const lines = value.split('\n');

    if (lines.length > 4 || lines.some(line => line.length > 25)) {
      setError('Нарушены правила создания вышивки');
    } else {
      setError('');
    }

    setDisplayText(value.trim() === '' ? 'Вышиварт' : value);
  };

  return (
    <div>
      <TextInput 
        textareaValue={textareaValue}
        handleTextareaChange={handleTextareaChange}
        error={error}
      />

      <SizeRadio 
        options={options}
        isRadioSelected={isRadioSelected}
        handleArtSizeChange={handleArtSizeChange}
      />

      <EmbroideryColorPicker 
        stitchingOptions={stitchingOptions}
        selectedColors={selectedColors}
        onSelectColor={onSelectColor}
      />

      <FontSelector 
        fonts={fonts}
        selectedArtFont={selectedArtFont}
        handleArtFontChange={handleArtFontChange}
      />

      <div className="container-field mb-6 w-full flex space-between items-center gap-4">
        <div className="container-field header-text w-48 text-2xl font-bold mb-2">ФОТО-НАШИВКА</div>
        {arts.map((art) => (
          <div
            key={art}
            className={`item-size min-w-40 h-10 text-2xl text-center ${
              selectedArt.is_art === (art === "убрать" ? "without-art" : "with-art") ? "selected" : ""
            }`}
            onClick={() => handleArtSelect("is_art", art === "убрать" ? "without-art" : "with-art")}
          >
            {art}
          </div>
        ))}
      </div>

      {selectedArt.is_art === 'with-art' && (
        <ImageUpload 
          handleImageChange={handleImageChange}
          previewUrl={previewUrl}
        />
      )}

      <hr className="border-t border-gray-300 my-4" />
      <div className="flex justify-between items-center w-full">
        <button 
          className="bg-gray-800 text-white px-6 py-2 rounded font-bold" 
          onClick={() => handleMenuClick(1)}
        >
          ← ИЗДЕЛИЕ
        </button>
        <p className="flex-grow text-center">money</p>
        <button 
          className="bg-gray-800 text-white px-6 py-2 rounded font-bold" 
          onClick={handleSubmit}
        >
          В КОРЗИНУ →
        </button>
      </div>
    </div>
  );
};

export default Menu2; 