import React, { useState, useEffect } from "react";
import "../styles/Constructor.css";
import api from '../api';

const Constructor = () => {
  const [categories, setCategories] = useState([]);
  const [imageUrl, setImageUrl] = useState("https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg");
  const [selectedMenu, setSelectedMenu] = useState(1);
  const [selectedItem, setSelectedItem] = useState(0);
  const [selectedColors, setSelectedColors] = useState({
    product: "Красный",
    art_color: "gray-800",
  });
  const [selectedItemSize, setItemSize] = useState({
    item_size: "XS",
  });
  const [textareaValue, setTextareaValue] = useState('');
  const [selectedArtSize, setSelectedArtSize] = useState(null);
  const [selectedArtFont, setSelectedArtFont] = useState({
    art_font: "стандартный"
  });
  const [fadeClass, setFadeClass] = useState("opacity-100");
  const [selectedArt, setSelectedArt] = useState({
    is_art: "without-art"
  });
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const itemTypes = [
    {
      name: "ФУТБОЛКА [iznanka]",
      colors: { 
        "gray-800": {
          "without-art": "https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg",
          "with-art": "https://static.tildacdn.com/stor3732-3338-4162-a165-636162393665/20457217.jpg"
        },
      }
    },
    {
      name: "ФУТБОЛКА [base]",
      colors: { 
        "gray-800": {
          "without-art": "https://static.tildacdn.com/tild3439-3166-4939-b638-316433393439/baze_.jpg",
          "with-art": "https://static.tildacdn.com/stor3734-6534-4163-b733-313365386664/80653543.jpg"
        },
      }
    },
    {
      name: "ЛОНГСЛИВ [choice]", 
      colors: { 
        "gray-800": {
          "without-art": "https://static.tildacdn.com/tild3732-3362-4066-b565-356633333263/_.jpg",
          "with-art": "https://static.tildacdn.com/stor3434-3863-4634-a361-356337333932/35194750.jpg"
        },
      }
    },
    {
      name: "СВИТШОТ [iznanka]",
      colors: { 
        "gray-800": {
          "without-art": "https://static.tildacdn.com/tild3333-3033-4561-b161-333864623036/_.jpg",
          "with-art": "https://static.tildacdn.com/stor3165-6539-4530-a235-346335653535/87538681.jpg"
        },
      }
    }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/catalog/items/?format=json");
        if (!response.ok) {
          throw new Error("Ошибка при загрузке данных");
        }

        const json = await response.json();

        const structuredData = Object.entries(json).map(([categoryName, categoryData]) => ({
          category: categoryName,
          items: Object.entries(categoryData).map(([size, colors]) => ({
            size,
            details: Object.entries(colors).map(([color, attributes]) => ({
              color,
              hex: attributes.hex,
              id: attributes.id,
              count: attributes.count
            })),
          })),
        }));

        setCategories(structuredData);
        setIsLoading(false);
      } catch (error) {
        console.error("Ошибка:", error);
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

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

  const changeImage = (newImage) => {
    setFadeClass("opacity-20");
    setTimeout(() => {
      setImageUrl(newImage);
      setFadeClass("opacity-100");
    }, 300);
  };

  const handleMenuClick = (menu) => setSelectedMenu(menu);

  const handleItemChange = (index) => {
    setSelectedItem(index);
    changeImage(itemTypes[index % itemTypes.length].colors["gray-800"][selectedArt.is_art]);
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

  const handleTextareaChange = (event) => {
    setTextareaValue(event.target.value);
  };

  const handleArtSizeChange = (event) => {
    setSelectedArtSize(event.target.value);
  };

  const handleArtFontChange = (type, font) => {
    setSelectedArtFont(prev => ({ ...prev, [type]: font }));
  };

  const handleArtSelect = (type, art) => {
    setSelectedArt(prev => ({ ...prev, [type]: art }));
    changeImage(itemTypes[selectedItem % itemTypes.length].colors["gray-800"][art]);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const isRadioSelected = (value) => selectedArtSize === value;

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center transition-opacity duration-500">
        <div className="text-2xl font-bold">ОЖИДАНИЕ</div>
      </div>
    );
  }

  return (
    <div className="constructor-container p-16">
      <div className="grid grid-cols-1 lg:grid-cols-5">
        <div className="col-span-3">
          <img
            src={imageUrl}
            alt="Футболка"
            className={`transition-opacity duration-300 ${fadeClass}`}
          />
        </div>

        <div className="max-w-full col-span-2">
          <h1 className="header-text text-5xl font-bold mb-4">
            {categoryNames[selectedItem] || "sample text"}
          </h1>

          <div className="mb-6 flex">
            <button
              className={`menu-header ${selectedMenu === 1 ? "active" : ""} font-bold text-xl w-full`}
              onClick={() => handleMenuClick(1)}
            >
              ИЗДЕЛИЕ
            </button>
            <button
              className={`menu-header ${selectedMenu === 2 ? "active" : ""} font-bold text-xl w-full`}
              onClick={() => handleMenuClick(2)}
            >
              ВЫШИВКА
            </button>
          </div>

          {selectedMenu === 1 ? (
            <Menu1
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
            <Menu2
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

const Menu1 = ({ selectedItem, handleItemChange, selectedColors, onSelectColor, selectedItemSize, handleItemSizeSelect, handleMenuClick, categoryNames, categoryItems }) => {
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

      <div className="container-field mb-6 flex flex-row gap-4">
        <div className="container-field header-text w-48 text-2xl font-bold mb-2">ЦВЕТ ИЗДЕЛИЯ</div>
        <div className="flex gap-4">
          {colorOptions.map((color) => (
            <div
              key={color.color}
              className={`color-circle ${selectedColors.product === color.color ? "selected" : ""}`}
              style={{ backgroundColor: color.hex }}
              onClick={() => onSelectColor("product", color.color)}
            />
          ))}
        </div>
      </div>

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

const Menu2 = ({ 
  textareaValue, 
  handleTextareaChange, 
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
  const options = ["0.8 - 1", "1.3 - 1.5"];
  const stitchingOptions = ["gray-800", "green-300", "pink-300"];
  const fonts = ["стандартный", "рукописный"];
  const arts = ["убрать", "добавить"];

  return (
    <div>
      <div className="container-field mb-6 flex flex-row gap-4">
        <div>
          <div className="container-field header-text w-48 text-2xl font-bold mb-2">СОДЕРЖАНИЕ</div>
          <p className="max-w-48 text-sm text-gray-400">
            до 25 символов в 1 строку. можно использовать любые печатные символы, кроме смайликов
          </p>
        </div>
        <textarea
          className="w-full h-32 px-3 py-2 border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 text-gray-700 resize-none"
          placeholder="Введите текст вышивки до 4 строчек или оставьте поле пустым, если вышивка не требуется."
          value={textareaValue}
          onChange={handleTextareaChange}
        />
      </div>

      <div className="container-field mb-6 flex flex-row gap-4">
        <div className="container-field header-text w-48 text-2xl font-bold mb-2">РАЗМЕР ВЫШИВКИ</div>
        {options.map((option) => (
          <label key={option} className="inline-flex items-center cursor-pointer gap-2">
            <input
              type="radio"
              name="example"
              value={option}
              checked={isRadioSelected(option)}
              onChange={handleArtSizeChange}
              className="hidden"
            />
            <span
              className={`w-6 h-6 border-2 ${isRadioSelected(option) ? "border-black" : "border-gray-500"} rounded-full flex items-center justify-center relative`}
            >
              <span
                className={`w-4 h-4 bg-black rounded-full absolute ${isRadioSelected(option) ? "opacity-100" : "opacity-0"}`}
              />
            </span>
            <p>{option} см</p>
          </label>
        ))}
      </div>

      <div className="container-field mb-6 flex flex-row items-center gap-4">
        <div className="container-field header-text w-48 text-2xl font-bold mb-2">ЦВЕТ ВЫШИВКИ</div>
        <div className="flex gap-4">
          {stitchingOptions.map((color) => (
            <div
              key={color}
              className={`color-circle bg-${color} ${selectedColors.art_color === color ? "selected" : ""}`}
              onClick={() => onSelectColor("art_color", color)}
            />
          ))}
        </div>
      </div>

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
        <div className="container-field mb-6 flex flex-row gap-4">
          <div>
            <div className="container-field header-text w-48 font-bold mb-2">ДОБАВИТЬ ФОТОГРАФИЮ</div>
            <p className="max-w-48 text-sm text-gray-400">
              тут какой-нибудь дисклеймер, типа фото ток такого-то формата
            </p>
          </div>
          <div className="flex flex-col gap-2">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 text-gray-700"
            />
            {previewUrl && (
              <div className="mt-2">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-w-[200px] max-h-[200px] object-contain"
                />
              </div>
            )}
          </div>
        </div>
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

export default Constructor;