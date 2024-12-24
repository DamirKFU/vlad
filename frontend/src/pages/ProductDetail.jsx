import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import '../styles/ProductDetail.css';

const ProductDetail = () => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`catalog/product/${productId}/`);
        setProduct(response.data);
        setLoading(false);
      } catch (err) {
        setError('Ошибка при загрузке данных о товаре');
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  const handleSizeChange = (size) => {
    setSelectedSize(size);
    setSelectedColor(''); // Сбросить выбранный цвет
    setQuantity(0); // Сбросить количество при смене размера
  };

  const handleColorChange = (color) => {
    setSelectedColor(color);
    if (product && selectedSize) {
      setQuantity(product.garments[selectedSize][color].count); // Установить количество для выбранного цвета
    }
  };

  const handleAddToCart = async () => {
    try {
        await api.post('catalog/cart/add/', {
            id_product: product.id,
            id_garment: product.garments[selectedSize][selectedColor].id
        });
        
        alert('Товар успешно добавлен в корзину');
    } catch (error) {
        console.error('Ошибка при добавлении в корзину:', error);
        alert('Ошибка при добавлении товара в корзину');
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p>{error}</p>;

  // Теперь просто используем product.image
  const imageUrl = product.image || '/placeholder.jpg'; // Если product.image не существует, используем заглушку

  return (
    <div className="product-detail">
      <h1>{product.name}</h1>
      <img src={imageUrl} alt={product.name} />
      <p>Цена: {product.price} руб</p>

      <div className="size-selection">
        <h3>Выберите размер:</h3>
        {Object.keys(product.garments).map(size => (
          <button key={size} onClick={() => handleSizeChange(size)}>
            {size}
          </button>
        ))}
      </div>

      {selectedSize && (
        <div className="color-selection">
          <h3>Выберите цвет:</h3>
          {Object.keys(product.garments[selectedSize]).map(color => (
            <button key={color} onClick={() => handleColorChange(color)}>
              {color}
            </button>
          ))}
        </div>
      )}

      {selectedColor && (
        <div className="quantity-selection">
          <h3>Количество: {quantity}</h3>
          <button onClick={handleAddToCart}>Добавить в корзину</button>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;