import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import '../styles/ProductDetail.css';

const ProductDetail = () => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`catalog/product/${productId}/`);
        const data = response.data;
        setProduct(data);
        
        // Проверяем наличие данных перед установкой значений по умолчанию
        if (data.garments && Object.keys(data.garments).length > 0) {
          const firstCategory = Object.keys(data.garments)[0];
          setSelectedCategory(firstCategory);
          
          if (data.garments[firstCategory] && Object.keys(data.garments[firstCategory]).length > 0) {
            const firstSize = Object.keys(data.garments[firstCategory])[0];
            setSelectedSize(firstSize);
            
            if (data.garments[firstCategory][firstSize] && 
                Object.keys(data.garments[firstCategory][firstSize]).length > 0) {
              const firstColor = Object.keys(data.garments[firstCategory][firstSize])[0];
              setSelectedColor(firstColor);
            }
          }
        }
        
        setLoading(false);
      } catch (err) {
        setError('Ошибка при загрузке данных о товаре');
        setLoading(false);
      }
    };
    fetchProduct();
  }, [productId]);

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    const firstSize = Object.keys(product.garments[category])[0];
    setSelectedSize(firstSize);
    const firstColor = Object.keys(product.garments[category][firstSize])[0];
    setSelectedColor(firstColor);
  };

  const handleSizeChange = (size) => {
    setSelectedSize(size);
    const firstColor = Object.keys(product.garments[selectedCategory][size])[0];
    setSelectedColor(firstColor);
  };

  const handleColorChange = (color) => {
    setSelectedColor(color);
  };

  const handleAddToCart = async () => {
    try {
      const selectedGarment = product.garments[selectedCategory][selectedSize][selectedColor].id;
      await api.post('catalog/cart/add/', {
        id_product: product.id,
        id_garment: selectedGarment
      });
      alert('Товар успешно добавлен в корзину');
    } catch (error) {
      console.error('Ошибка при добавлении в корзину:', error);
      alert('Ошибка при добавлении товара в корзину');
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p>{error}</p>;
  if (!product) return null;

  const hasImages = selectedCategory && 
                   selectedColor && 
                   product.images && 
                   product.images[selectedCategory] && 
                   product.images[selectedCategory][selectedColor] && 
                   product.images[selectedCategory][selectedColor].length > 0;

  return (
    <div className={`product-detail ${!hasImages ? 'no-images' : ''}`}>
      {hasImages && (
        <div className="product-images">
          {selectedCategory && 
           selectedColor && 
           product.images && 
           product.images[selectedCategory] && 
           product.images[selectedCategory][selectedColor] && 
           product.images[selectedCategory][selectedColor].length > 0 ? (
            <>
              {product.images[selectedCategory][selectedColor].map((imageUrl, index) => (
                <div key={index} className="product-image">
                  <img 
                    src={imageUrl} 
                    alt={`${product.name} - ${selectedCategory} ${selectedColor} ${index + 1}`} 
                  />
                </div>
              ))}
            </>
          ) : null}
        </div>
      )}
      
      <div className="product-info">
        <h2>{product.name}</h2>
        <p className="price">Цена: {product.price} ₽</p>

        <div className="options-container">
          <div className="categories">
            <h3>Категория</h3>
            <div className="category-buttons">
              {Object.keys(product.garments).map(category => (
                <button
                  key={category}
                  onClick={() => handleCategoryChange(category)}
                  className={selectedCategory === category ? 'selected' : ''}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="sizes">
            <h3>Размер</h3>
            <div className="size-buttons">
              {Object.keys(product.garments[selectedCategory] || {}).map(size => (
                <button
                  key={size}
                  onClick={() => handleSizeChange(size)}
                  className={selectedSize === size ? 'selected' : ''}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          <div className="colors">
            <h3>Цвет</h3>
            <div className="color-buttons">
              {Object.entries(product.garments[selectedCategory][selectedSize] || {}).map(([colorName, data]) => (
                <button
                  key={colorName}
                  onClick={() => handleColorChange(colorName)}
                  className={`color-button ${selectedColor === colorName ? 'selected' : ''}`}
                  title={`${colorName} (${data.count} шт.)`}
                >
                  <span 
                    className="color-swatch" 
                    style={{ backgroundColor: data.hex }}
                  />
                  <span className="color-name">{colorName}</span>
                  <span className="color-count">{data.count} шт.</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <button 
          onClick={handleAddToCart} 
          className="add-to-cart-button"
          disabled={!selectedColor || !selectedSize}
        >
          Добавить в корзину
        </button>
      </div>
    </div>
  );
};

export default ProductDetail;