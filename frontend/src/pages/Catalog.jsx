import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { API_URL } from '../constants/core'; // Импортируем API_URL
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
      <div className="catalog-empty text-center">
        <h2>Товары не найдены</h2>
        <p>В данный момент каталог пуст</p>
      </div>
    );
  }

  return (
    <div className="container catalog">
      <div className="catalog-header text-center mb-4">
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

      <div className="catalog-filters mb-4">
        <button className="btn btn-outline-primary me-2">Промо</button>
        <button className="btn btn-outline-primary me-2">Стандарт</button>
        <button className="btn btn-outline-primary me-2">Плотные</button>
        <button className="btn btn-outline-primary me-2">Премиум</button>
        <button className="btn btn-outline-primary me-2">С экстрастоном</button>
        <button className="btn btn-outline-primary me-2">Крашеные</button>
        <button className="btn btn-outline-primary">Поло</button>
      </div>

      <div className="row">
        {products.map(product => (
          <div key={product.id} className="col-md-4 mb-4">
            <div className="card product-card">
              <div className="product-image">
                {product.image ? (
                  <img 
                    src={`${API_URL}${product.image}`} // Используем API_URL
                    alt={product.name}
                    className="card-img-top"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = '/placeholder.jpg';
                    }}
                  />
                ) : (
                  <div className="product-image-placeholder card-img-top">
                    Нет изображения
                  </div>
                )}
              </div>
              <div className="card-body">
                <h3 className="product-title">{product.name}</h3>
                <p className="product-price">{product.price} руб</p>
                <Link to={`/product/${product.id}`} className="btn btn-primary">
                  Подробнее
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasMore && (
        <div className="text-center">
          <button 
            onClick={() => setPage(prev => prev + 1)} 
            className="btn btn-outline-primary"
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
