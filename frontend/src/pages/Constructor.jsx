import React, { useState } from "react";
import "../styles/Constructor.css";

const Constructor = () => {
  const itemTypes = [
    {
      name: "ФУТБОЛКА [iznanka]",
      colors: { "gray-800": "https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg" }
    },
    {
      name: "ФУТБОЛКА [base]",
      colors: { "gray-800": "https://static.tildacdn.com/tild3439-3166-4939-b638-316433393439/baze_.jpg" }
    },
    {
      name: "ЛОНГСЛИВ [choice]",
      colors: { "gray-800": "https://static.tildacdn.com/tild3732-3362-4066-b565-356633333263/_.jpg" }
    },
    {
      name: "СВИТШОТ [iznanka]",
      colors: { "gray-800": "https://static.tildacdn.com/tild3333-3033-4561-b161-333864623036/_.jpg" }
    }
  ]
  const [imageUrl, setImageUrl] = useState(
    "https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg"
  );
  const [itemName, setItemName] = useState(
    "ФУТБОЛКА [iznanka]"
  );
  const [selectedMenu, setSelectedMenu] = useState(1);
  const [selectedItem, setSelectedItem] = useState(0);
  const [selectedColors, setSelectedColors] = useState({
    product: "gray-400",
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

  const getVariables = [
    { itemName: itemName },
    { imageUrl: imageUrl },
    { productColor: selectedColors.product },
    { artColor: selectedColors.art_color },
    { itemSize: selectedItemSize.item_size },
    { textareaContent: textareaValue },
    { artSize: selectedArtSize },
    { artFont: selectedArtFont.art_font }
  ];

  const changeImage = (image) => {
    setImageUrl(image);
  };

  const handleMenuClick = (menu) => {
    setSelectedMenu(menu);
  };

  const handleItemChange = (index) => {
    setSelectedItem(index);
    changeImage(itemTypes[index].colors["gray-800"]);
    setItemName(itemTypes[index].name);
  };

  const handleColorSelect = (type, color) => {
    setSelectedColors((prev) => ({ ...prev, [type]: color }));
    console.log(color);
  };

  const handleItemSizeSelect = (type, size) => {
    console.log(selectedItemSize);
    setItemSize(prev => ({ ...prev, [type]: size }));
  };

  const handleTextareaChange = (event) => {
    console.log(event.target.value)
    setTextareaValue(event.target.value);
  };

  const handleArtSizeChange = (event) => {
    setSelectedArtSize(event.target.value);
  };

  const handleArtFontChange = (type, font) => {
    setSelectedArtFont(prev => ({ ...prev, [type]: font }));
  };

  const isRadioSelected = (value) => selectedArtSize === value;

  return (
    <div className="p-16">
      <div className="grid grid-cols-1 lg:grid-cols-5">
        {/* Product Image */}
        <div className="col-span-3">
          <img
            src={imageUrl}
            alt="Футболка"
          />
        </div>

        {/* Product Details */}
        <div className="max-w-full col-span-2">
          <h1 className="header-text text-5xl font-bold mb-4">{itemName}</h1>

          {/* Tabs */}
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

          {/* Menu Content */}
          {selectedMenu === 1 && (
            <Menu1
              selectedItem={selectedItem}
              handleItemChange={handleItemChange}
              selectedColors={selectedColors}
              onSelectColor={handleColorSelect}
              selectedItemSize={selectedItemSize}
              handleItemSizeSelect={handleItemSizeSelect}
              handleMenuClick={handleMenuClick}
            />
          )}
          {selectedMenu === 2 && (
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
              getVariables={getVariables}
            />
          )}
        </div>
      </div>

      {/* temporary*/}
      <div className="hidden">
        <div className="bg-gray-400"></div>
        <div className="bg-gray-800"></div>
        <div className="bg-pink-300"></div>
        <div className="bg-green-300"></div>
      </div>
    </div>
  );
};

const Menu1 = ({ selectedItem, handleItemChange, selectedColors, onSelectColor, selectedItemSize, handleItemSizeSelect, handleMenuClick }) => {
  const colorOptions = ["gray-400", "gray-800", "pink-300"];
  const itemTypes = ["ФУТБОЛКА [iznanka]", "ФУТБОЛКА [base]", "ЛОНГСЛИВ [choice]", "СВИТШОТ [iznanka]"];
  const size = ["XS", "XL", "L-XL", "xxx"]

  return (
    <>
      {/* Choose item */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-44 text-2xl font-bold mb-2">ИЗДЕЛИЕ</div>
        <div className="product-options flex flex-col">
          {itemTypes.map((option, index) => (
            <label
              key={index}
              className={`text-xl text-gray-400 mb-2 p-2 cursor-pointer rounded-md ${selectedItem === index ? 'border-2 border-black' : ''
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

      {/* Product Color */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-48 text-2xl font-bold mb-2">ЦВЕТ ИЗДЕЛИЯ</div>
        <div className="flex gap-4">
          {colorOptions.map((color) => (
            <div
              key={color}
              className={`color-circle bg-${color} ${selectedColors.product === color ? "selected" : ""}`}
              onClick={() => onSelectColor("product", color)}
            ></div>
          ))}
        </div>
      </div>

      {/* Size choose */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-48 text-2xl font-bold mb-2">РАЗМЕР</div>
        <div className="flex gap-4">
          {size.map((size) => (
            <div
              key={size}
              className={`item-size min-w-10 h-8 text-xl text-center ${selectedItemSize.item_size === size ? "selected" : ""
                }`}
              onClick={() => handleItemSizeSelect("item_size", size)}
            >
              {size}
            </div>
          ))}
        </div>
      </div>

      <hr className="border-t border-gray-300 my-4"></hr>
      <div className="flex justify-end">
        <button className="bg-gray-800 text-white px-6 py-2 rounded font-bold" onClick={() => handleMenuClick(2)}>ВЫШИВКА →</button>
      </div>
    </>
  );
};

const Menu2 = ({ textareaValue, handleTextareaChange, isRadioSelected, handleArtSizeChange, selectedColors, onSelectColor, handleMenuClick, selectedArtFont, handleArtFontChange, getVariables }) => {
  const options = ["0.8 - 1", "1.3 - 1.5"];
  const stitchingOptions = ["gray-800", "green-300", "pink-300"];
  const fonts = ["стандартный", "рукописный"]

  return (
    <div>
      {/* Text Area */}
      <div className="mb-6 flex flex-row gap-4">
        <div>
          <div className="w-48 text-2xl font-bold mb-2">СОДЕРЖАНИЕ</div>
          <p className="max-w-48 text-sm text-gray-400">
            до 25 символов в 1 строку. можно использовать любые печатные символы, кроме смайликов
          </p>
        </div>
        <textarea
          className="w-full h-32 px-3 py-2 border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 text-gray-700 resize-none"
          placeholder="Введите текст вышивки до 4 строчек или оставьте поле пустым, если вышивка не требуется."
          value={textareaValue}
          onChange={handleTextareaChange}
        ></textarea>
      </div>

      {/* Radio-Buttons */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-48 text-2xl font-bold mb-2">РАЗМЕР ВЫШИВКИ</div>
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
              ></span>
            </span>
            <p>{option} см</p>
          </label>
        ))}
      </div>

      {/* Art Color */}
      <div className="mb-6 flex flex-row items-center gap-4">
        <div className="w-48 text-2xl font-bold mb-2">ЦВЕТ ВЫШИВКИ</div>
        <div className="flex gap-4">
          {stitchingOptions.map((color) => (
            <div
              key={color}
              className={`color-circle bg-${color} ${selectedColors.art_color === color ? "selected" : ""
                }`}
              onClick={() => onSelectColor("art_color", color)}
            ></div>
          ))}
        </div>
      </div>

      {/* Art font */}
      <div className="mb-6 w-full flex space-between items-center gap-4">
        <div className="w-48 text-2xl font-bold mb-2">ШРИФТ</div>
        {fonts.map((font) => (
          <div
            key={font}
            className={`item-size min-w-40 h-10 text-2xl text-center ${selectedArtFont.art_font === font ? "selected" : ""
              }`}
            onClick={() => handleArtFontChange("art_font", font)}
          >
            {font}
          </div>
        ))}
      </div>

      <hr className="border-t border-gray-300 my-4"></hr>
      <div className="flex justify-between items-center w-full">
        <button className="bg-gray-800 text-white px-6 py-2 rounded font-bold" onClick={() => handleMenuClick(1)}>← ИЗДЕЛИЕ</button>
        <p className="flex-grow text-center">money</p>
        <button className="bg-gray-800 text-white px-6 py-2 rounded font-bold" onClick={() => console.log(getVariables)}>В КОРЗИНУ →</button>
      </div>
    </div>
  )
};

export default Constructor;