import React from 'react';

const ErrorMessage = ({ message = "Произошла ошибка", onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-4">
      <div className="text-red-600 text-xl font-bold mb-2">Ошибка</div>
      <p className="text-gray-600 text-center mb-4">{message}</p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="bg-gray-800 text-white px-6 py-2 rounded font-bold hover:bg-gray-700"
        >
          Попробовать снова
        </button>
      )}
    </div>
  );
};

export default ErrorMessage; 