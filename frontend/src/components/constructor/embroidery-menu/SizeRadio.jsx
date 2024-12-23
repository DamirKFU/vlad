import React from 'react';

const SizeRadio = ({ options, isRadioSelected, handleArtSizeChange }) => {
  return (
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
  );
};

export default SizeRadio; 