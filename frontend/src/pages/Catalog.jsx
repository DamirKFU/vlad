import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/Catalog.css';

const Catalog = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('catalog/products/');
        console.log('Products data:', response.data);
        
        setProducts(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.response?.data?.message || 'Ошибка при загрузке данных');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="catalog-loading">
        <div className="loading-spinner"></div>
        <p>Загрузка каталога...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="catalog-error">
        <h2>Произошла ошибка</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Попробовать снова
        </button>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="catalog-empty">
        <h2>Товары не найдены</h2>
        <p>В данный момент каталог пуст</p>
      </div>
    );
  }

  return (
    <div className="catalog">
      <div className="catalog-header">
        <h1>Футболки</h1>
        <p className="catalog-description">
          Наши футболки различаются по плотности, от 140 г до 300 г. Представлены в различных вариантах кроя: свободный, стандартный, свободный реглан.
          Также в своем экспериментальном красильном цехе мы создаем лимитированные партии футболок.
        </p>
      </div>

      <div className="catalog-filters">
        <button className="filter-btn">Промо</button>
        <button className="filter-btn">Стандарт</button>
        <button className="filter-btn">Плотные</button>
        <button className="filter-btn">Премиум</button>
        <button className="filter-btn">С экстастаном</button>
        <button className="filter-btn">Крашеные</button>
        <button className="filter-btn">Поло</button>
      </div>

      <div className="catalog-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <div className="product-image">
              {product.image ? (
                <img 
                  src={product.image} 
                  alt={product.name}
                  onError={(e) => {
                    e.target.onerror = null; // Предотвращаем бесконечную рекурсию
                    e.target.src = '/placeholder.jpg'; // Путь к placeholder изображению
                  }}
                />
              ) : (
                <div className="product-image-placeholder">
                  Нет изображения
                </div>
              )}
            </div>
            <div className="product-info">
              <h3 className="product-title">{product.name}</h3>
              <p className="product-price">{product.price} руб</p>
              <button className="add-to-cart-btn">
                Подробнее
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Catalog;
