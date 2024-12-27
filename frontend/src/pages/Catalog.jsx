import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import '../styles/Catalog.css';
import Preloader from '../components/common/Preloader';
import ErrorMessage from '../components/common/ErrorMessage';

const Catalog = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`catalog/products/?page=${page}`);
        setProducts(prev => [...prev, ...response.data.data.results]);
        setTotalCount(response.data.data.count);
        setHasMore(!!response.data.data.next);
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.message || 'Произошла ошибка при загрузке данных');
        setLoading(false);
      }
    };
    fetchData();
  }, [page]);

  if (loading) {
    return <Preloader message="Загрузка каталога..." />;
  }

  if (error) {
    return <ErrorMessage 
      message={error} 
      onRetry={() => window.location.reload()} 
    />;
  }

  // Если данных нет
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
          Наши футболки различаются по плотности, от 140 г до 300 г. 
          Представлены в различных вариантах кроя: свободный, стандартный, 
          свободный реглан. Также в своем экспериментальном красильном цехе 
          мы создаем лимитированные партии футболок.
        </p>
        <div className="catalog-count">
          Всего товаров: {totalCount}
        </div>
      </div>

      <div className="catalog-filters">
        <button className="filter-btn">Промо</button>
        <button className="filter-btn">Стандарт</button>
        <button className="filter-btn">Плотные</button>
        <button className="filter-btn">Премиум</button>
        <button className="filter-btn">С экстастаном</button>
        <button className="filter-btn">Кршены</button>
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
                    e.target.onerror = null;
                    e.target.src = '/placeholder.jpg';
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
              <Link to={`/product/${product.id}`} className="add-to-cart-btn">
                Подробнее
              </Link>
            </div>
          </div>
        ))}
      </div>

      {hasMore && (
        <div className="load-more">
          <button 
            onClick={() => setPage(prev => prev + 1)} 
            className="load-more-btn"
            disabled={loading}
          >
            {loading ? 'Загрузка...' : 'Загрузить еще'}
          </button>
        </div>
      )}
    </div>
  );
};

export default Catalog;
