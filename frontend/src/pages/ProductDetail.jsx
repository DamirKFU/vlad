import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { API_URL } from '../constants/core';
import '../styles/ProductDetail.css';
import '../styles/bootstrap-5.3.3-dist/css/bootstrap.min.css';
import ErrorMessage from '../components/common/ErrorMessage';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`catalog/products/${productId}/`);
        setProduct(response.data.data);
        setLoading(false);

        // Установка значений по умолчанию
        if (response.data.data.garments.length > 0) {
          const firstGarment = response.data.data.garments[0];
          setSelectedCategory(firstGarment.category.name);
          setSelectedSize(firstGarment.size);
          setSelectedColor(firstGarment.color.name);
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Произошла ошибка при загрузке данных');
        setLoading(false);
      }
    };
    fetchProduct();
  }, [productId, navigate]);

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setSelectedSize(''); // Сброс размера при смене категории
    setSelectedColor(''); // Сброс цвета при смене категории
  };

  const handleSizeChange = (size) => {
    setSelectedSize(size);
    // Проверка доступных цветов для нового размера
    const availableColorsForSize = product.garments
      .filter(garment => garment.category.name === selectedCategory && garment.size === size)
      .map(garment => ({
        name: garment.color.name,
        hex: garment.color.hex,
        count: garment.count
      }));

    // Если выбранный цвет недоступен, выбираем первый доступный цвет
    if (!availableColorsForSize.some(color => color.name === selectedColor)) {
      setSelectedColor(availableColorsForSize.length > 0 ? availableColorsForSize[0].name : '');
    }
  };

  const handleColorChange = (color) => {
    setSelectedColor(color);
  };

  const handleAddToCart = async () => {
    if (!selectedCategory || !selectedSize || !selectedColor) return;

    try {
      const selectedGarment = product.garments.find(garment => 
        garment.category.name === selectedCategory &&
        garment.size === selectedSize &&
        garment.color.name === selectedColor
      );

      await api.post('catalog/cart/add/', {
        id_product: product.id,
        id_garment: selectedGarment.id
      });
      alert('Товар успешно добавлен в корзину');
    } catch (err) {
      console.error('Ошибка при добавлении в корзину:', err);
      alert('Ошибка при добавлении товара в корзину');
    }
  };

  if (loading) {
    return <p>Загрузка...</p>;
  }

  if (error) {
    return <ErrorMessage 
      message={error} 
      onRetry={() => window.location.reload()} 
    />;
  }

  const availableSizes = product.garments
    .filter(garment => garment.category.name === selectedCategory)
    .map(garment => garment.size);

  const availableColors = product.garments
    .filter(garment => garment.category.name === selectedCategory && garment.size === selectedSize)
    .map(garment => ({
      name: garment.color.name,
      hex: garment.color.hex,
      count: garment.count
    }));

  const uniqueCategories = Array.from(new Set(product.garments.map(garment => garment.category.name)));

  const additionalImages = product.additional_images.filter(img => 
    img.category.name === selectedCategory && img.color.name === selectedColor
  );

  return (
    <div className="product-detail">
      <div className="product-images">
        <div className="image-container" style={{ backgroundColor: 'black', padding: '10px', borderRadius: '5px' }}>
          <img 
            src={`${API_URL}${product.image}`} 
            alt={product.name} 
            className="main-image"
          />
        </div>
        {additionalImages.length > 0 ? (
          additionalImages.map((img, idx) => (
            <div key={idx} className="image-container" style={{ backgroundColor: 'black', padding: '10px', borderRadius: '5px' }}>
              <img 
                src={`${API_URL}${img.image}`} 
                alt={`${product.name} - дополнительное изображение ${idx + 1}`} 
                className="additional-image"
              />
            </div>
          ))
        ) : null}
      </div>

      <div className="product-info">
        <h2>{product.name}</h2>
        <p className="price">Цена: {product.price} ₽</p>

        <div className="garment-options">
          <h3>Выберите категорию</h3>
          {uniqueCategories.map((category) => (
            <button 
              key={category} 
              onClick={() => handleCategoryChange(category)}
              className={`garment-button btn ${selectedCategory === category ? 'btn-primary' : 'btn-outline-primary'}`}
            >
              {category}
            </button>
          ))}
        </div>

        {selectedCategory && (
          <>
            <h3>Выберите размер</h3>
            {Array.from(new Set(availableSizes)).map((size) => (
              <button 
                key={size} 
                onClick={() => handleSizeChange(size)}
                className={`garment-button btn ${selectedSize === size ? 'btn-primary' : 'btn-outline-primary'}`}
              >
                {size}
              </button>
            ))}
          </>
        )}

        {selectedSize && (
          <>
            <h3>Выберите цвет</h3>
            <div className="color-options">
              {availableColors.map((color) => (
                <button 
                  key={color.name} 
                  onClick={() => handleColorChange(color.name)}
                  className={`color-button ${selectedColor === color.name ? 'selected' : ''}`}
                  style={{ backgroundColor: color.hex, borderRadius: '50%', width: '40px', height: '40px', margin: '5px', border: 'none' }}
                  title={`${color.name} (${color.count} шт.)`}
                />
              ))}
            </div>
          </>
        )}

        <button 
          onClick={handleAddToCart} 
          className="add-to-cart-button btn btn-success"
          disabled={!selectedCategory || !selectedSize || !selectedColor}
        >
          Добавить в корзину
        </button>
      </div>
    </div>
  );
};

export default ProductDetail;