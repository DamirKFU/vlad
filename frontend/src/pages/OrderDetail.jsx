import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import '../styles/OrderDetail.css';
import Preloader from '../components/common/Preloader';
import ErrorMessage from '../components/common/ErrorMessage';

const OrderDetail = () => {
    const { orderId } = useParams();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                const response = await api.get(`catalog/orders/${orderId}/`);
                setOrder(response.data.data);
                setLoading(false);
            } catch (err) {
                setError(err.response?.data?.message || 'Ошибка при загрузке заказа');
                setLoading(false);
            }
        };

        fetchOrder();
    }, [orderId]);

    if (loading) return <Preloader message="Загрузка заказа..." />;
    if (error) return <ErrorMessage message={error} />;
    if (!order) return <ErrorMessage message="Заказ не найден" />;

    return (
        <div className="checkout-container">
            <h1>Заказ #{order.id}</h1>
            
            <div className="checkout-items">
                {order.items.map(item => (
                    <div key={item.id} className="checkout-item">
                        <div className="item-image">
                            {item.image ? (
                                <img 
                                    src={item.image} 
                                    alt={item.name}
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
                        <div className="item-info">
                            <h3>{item.name}</h3>
                            <div className="item-details">
                                <span>{item.category}</span>
                                <span className="color-dot" style={{ backgroundColor: item.color }}></span>
                                <span>{item.size}</span>
                                <span>×{item.quantity}</span>
                            </div>
                            <div className="item-price">
                                {item.total_price} ₽
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="delivery-section">
                <h2>Статус заказа</h2>
                <div className={`order-status status-${order.status}`}>
                    {order.status_display}
                </div>
                <div className={`payment-status payment-status-${order.payment_status}`}>
                    {order.payment_status_display}
                </div>
            </div>

            <div className="delivery-section">
                <h2>Адрес доставки</h2>
                <div className="address-display">
                    {order.address}
                </div>
            </div>

            <div className="delivery-section">
                <h2>Телефон</h2>
                <div className="phone-display">
                    {order.phone}
                </div>
            </div>

            <div className="checkout-summary">
                <div className="total-info">
                    <h2>Итого к оплате:</h2>
                    <span className="total-price">{order.total_sum} ₽</span>
                </div>
                {order.status === 'WP' && order.confirmation_url && (
                    <a 
                        href={order.confirmation_url}
                        className="pay-order-btn"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Оплатить заказ
                    </a>
                )}
            </div>
        </div>
    );
};

export default OrderDetail; 