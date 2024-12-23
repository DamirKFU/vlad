import React from 'react';

const TextInput = ({ textareaValue, handleTextareaChange, error }) => {
  return (
    <div className="container-field mb-6 flex flex-row gap-4">
      <div>
        <div className="container-field header-text w-48 text-2xl font-bold mb-2">СОДЕРЖАНИЕ</div>
        <p className="max-w-48 text-sm text-gray-400">
          до 25 символов в 1 строке. можно использовать любые печатные символы, кроме смайликов
        </p>
      </div>
      <div className="flex flex-col w-full">
        <textarea
          className="w-full h-32 px-3 py-2 border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300 text-gray-700 resize-none"
          placeholder="Введите текст вышивки до 4 строчек или оставьте поле пустым, если вышивка не требуется."
          value={textareaValue}
          onChange={(e) => handleTextareaChange(e.target.value)}
        />
        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
};

export default TextInput; 