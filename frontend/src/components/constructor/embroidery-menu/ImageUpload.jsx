import React from 'react';

const ImageUpload = ({ handleImageChange, previewUrl }) => {
  return (
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
  );
};

export default ImageUpload; 