import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/OrderHistory.css';
import Preloader from '../components/common/Preloader';
import ErrorMessage from '../components/common/ErrorMessage';

const OrderHistory = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await api.get('catalog/orders/history/');
                setOrders(response.data);
                setLoading(false);
            } catch (err) {
                setError(err.response?.data?.message || 'Ошибка при загрузке заказов');
                setLoading(false);
            }
        };

        fetchOrders();
    }, []);

    const handleCancelOrder = async (orderId) => {
        try {
            await api.post(`catalog/order/${orderId}/cancel/`);
            setOrders(orders.map(order => 
                order.id === orderId 
                    ? { ...order, status: 'CN', status_display: 'Отменён' }
                    : order
            ));
        } catch (err) {
            alert(err.response?.data?.error || 'Ошибка при отмене заказа');
        }
    };

    if (loading) return <Preloader message="Загрузка истории заказов..." />;
    if (error) return <ErrorMessage message={error} />;

    return (
        <div className="order-history">
            <div className="cart-header">
                <h1>История заказов</h1>
            </div>
            
            {orders.length === 0 ? (
                <div className="no-orders">
                    <p>У вас пока нет заказов</p>
                </div>
            ) : (
                <div className="orders-list">
                    {orders.map(order => (
                        <div key={order.id} className="order-card">
                            <div className="order-header">
                                <div className="order-info">
                                    <h2>Заказ №{order.id}</h2>
                                    <p className="order-date">
                                        {new Date(order.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                                <div className="order-status">
                                    <span className={`status-badge status-${order.status}`}>
                                        {order.status_display}
                                    </span>
                                    {order.status === 'WP' && (
                                        <button 
                                            className="cancel-order-btn"
                                            onClick={() => handleCancelOrder(order.id)}
                                        >
                                            Отменить заказ
                                        </button>
                                    )}
                                </div>
                            </div>

                            <div className="order-address">
                                <span className="address-label">Адрес доставки:</span>
                                <span className="address-value">{order.address}</span>
                            </div>

                            <div className="order-items">
                                {order.items.map(item => (
                                    <div key={item.id} className="order-item">
                                        <div className="item-image">
                                            {item.image ? (
                                                <img src={item.image} alt={item.name} />
                                            ) : (
                                                <div className="no-image">Нет фото</div>
                                            )}
                                        </div>
                                        <div className="item-details">
                                            <h3>{item.name}</h3>
                                            <div className="item-specs">
                                                <span className="spec-tag">{item.size}</span>
                                                <span className="spec-tag category-tag">{item.category}</span>
                                                <span 
                                                    className="color-tag" 
                                                    style={{ backgroundColor: item.color }}
                                                />
                                            </div>
                                            <div className="item-price-details">
                                                <div className="quantity-info">
                                                    <span className="quantity-label">Количество:</span>
                                                    <span className="quantity-value">{item.quantity}</span>
                                                </div>
                                                <div className="price-calculation">
                                                    <span className="unit-price">{item.price} ₽</span>
                                                    <span className="multiply-symbol">×</span>
                                                    <span className="quantity">{item.quantity}</span>
                                                    <span className="equals-symbol">=</span>
                                                    <span className="total-price">{item.total_price} ₽</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="order-footer">
                                <div className="order-total">
                                    Итого: {order.total_sum} ₽
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OrderHistory; 