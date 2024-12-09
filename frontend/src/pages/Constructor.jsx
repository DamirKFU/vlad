import React, { useState } from "react";
import "../styles/Constructor.css";

const Constructor = () => {
  const [selectedMenu, setSelectedMenu] = useState(1);
  const [selectedColors, setSelectedColors] = useState({
    product: "white",
    stitching: "black",
  });

  const handleMenuClick = (menu) => {
    setSelectedMenu(menu);
  };

  const handleColorSelect = (type, color) => {
    setSelectedColors((prev) => ({ ...prev, [type]: color }));
  };

  return (
    <div className="p-16">
      <div className="grid grid-cols-1 lg:grid-cols-5">
        {/* Product Image */}
        <div className="col-span-3">
          <img
            src="https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg"
            alt="Футболка"
          />
        </div>

        {/* Product Details */}
        <div className="max-w-full col-span-2">
          <h1 className="header-text text-5xl font-bold mb-4">ФУТБОЛКА [iznanka]</h1>

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
              selectedColors={selectedColors}
              onSelectColor={handleColorSelect}
            />
          )}
          {selectedMenu === 2 && <Menu2 />}
        </div>
      </div>
    </div>
  );
};

const Menu1 = ({ selectedColors, onSelectColor }) => {
  const colorOptions = ["white", "gray", "pink"];
  const stitchingOptions = ["black", "green", "pink"];

  return (
    <>
      {/* Product Type */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-44 text-2xl font-bold mb-2">ИЗДЕЛИЕ</div>
        <div className="product-options flex flex-col">
          {["ФУТБОЛКА [iznanka]", "ФУТБОЛКА [base]", "ЛОНГСЛИВ [choice]", "СВИТШОТ [iznanka]"].map(
            (option, index) => (
              <label key={index} className="text-xl">
                <input
                  type="radio"
                  name="product"
                  defaultChecked={index === 0}
                />
                {option}
              </label>
            )
          )}
        </div>
      </div>

      {/* Product Color */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-48 text-2xl font-bold mb-2">ЦВЕТ ИЗДЕЛИЯ</div>
        <div className="flex gap-4">
          {colorOptions.map((color) => (
            <div
              key={color}
              className={`color-circle bg-${color} ${
                selectedColors.product === color ? "selected" : ""
              }`}
              onClick={() => onSelectColor("product", color)}
            ></div>
          ))}
        </div>
      </div>

      {/* Stitching Color */}
      <div className="mb-6 flex flex-row gap-4">
        <div className="w-48 text-2xl font-bold mb-2">ЦВЕТ ШВОВ</div>
        <div className="flex gap-4">
          {stitchingOptions.map((color) => (
            <div
              key={color}
              className={`color-circle bg-${color} ${
                selectedColors.stitching === color ? "selected" : ""
              }`}
              onClick={() => onSelectColor("stitching", color)}
            ></div>
          ))}
        </div>
      </div>
    </>
  );
};

const Menu2 = () => (
  <div>
    <div className="mb-6 flex flex-row gap-4">
      <div>
        <div className="w-48 text-2xl font-bold mb-2">ЦВЕТ ШВОВ</div>
        <p className="max-w-48 text-sm text-gray-400">
          до 25 символов в 1 строку. можно использовать любые печатные символы, кроме смайликов
        </p>
      </div>
      <textarea
        className="w-full h-32 px-3 py-2 border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 text-gray-700 resize-none"
        placeholder="Введите текст вышивки до 4 строчек или оставьте поле пустым, если вышивка не требуется."
      ></textarea>
    </div>
    <div className="mb-6 flex flex-row gap-4">
      <div className="w-48 text-2xl font-bold mb-2">РАЗМЕР ВЫШИВКИ</div>
      <p>TE</p>
    </div>
  </div>
);

export default Constructor;