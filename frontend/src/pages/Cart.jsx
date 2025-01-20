import React, { useState, useEffect } from 'react';
import api from '../api';
import { API_URL } from '../constants/core';
import '../styles/Cart.css';
import '../styles/bootstrap-5.3.3-dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';

const Cart = () => {
    const [cartItems, setCartItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCart();
    }, []);

    const fetchCart = async () => {
        try {
            const response = await api.get('catalog/cart/');
            setCartItems(response.data.data.items);
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.message || 'Ошибка при загрузке корзины');
            setLoading(false);
        }
    };

    const handleUpdateQuantity = async (itemId, newQuantity) => {
        try {
            const response = await api.patch(`catalog/cart/item/${itemId}/`, {
                quantity: newQuantity
            });
            
            // Проверяем статус ответа
            if (response.status === 200) {
                setCartItems(prevItems => 
                    prevItems.map(item => 
                        item.id === itemId 
                            ? { 
                                ...item, 
                                quantity: response.data.data.quantity,
                                total_price: response.data.data.total_price
                            }
                            : item
                    )
                );
            }
        } catch (err) {
            console.error('Ошибка при обновлении количества:', err);
        }
    };

    const handleRemoveItem = async (itemId) => {
        try {
            const response = await api.delete(`catalog/cart/item/${itemId}/`);
            
            // Проверяем статус ответа
            if (response.status === 200) {
                setCartItems(prevItems => prevItems.filter(item => item.id !== itemId));
            }
        } catch (err) {
            console.error('Ошибка при удалении товара:', err);
        }
    };

    const handleCheckout = () => {
        const totalSum = cartItems.reduce((sum, item) => sum + item.total_price, 0);
        navigate('/checkout', { 
            state: { cartItems, totalSum } 
        });
    };

    if (loading) return <p>Загрузка...</p>;
    if (error) return <p>{error}</p>;

    const totalSum = cartItems.reduce((sum, item) => sum + item.total_price, 0);

    return (
        <div className="cart-container">
            <h1>Корзина</h1>
            {cartItems.length === 0 ? (
                <p>Ваша корзина пуста</p>
            ) : (
                <>
                    <div className="cart-items">
                        {cartItems.map(item => (
                            <div key={item.id} className="cart-item d-flex align-items-center mb-3">
                                <div className="cart-item-image me-3">
                                    {item.product.image ? (
                                        <img 
                                            src={`${API_URL}${item.product.image}`} 
                                            alt={item.product.name}
                                            className="img-fluid"
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
                                <div className="cart-item-details flex-grow-1">
                                    <div className="cart-item-header d-flex justify-content-between">
                                        <h3>{item.product.name}</h3>
                                        <button 
                                            className="remove-button btn btn-danger"
                                            onClick={() => handleRemoveItem(item.id)}
                                            aria-label="Удалить товар"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                    <div className="cart-item-specs">
                                        <div className="spec-group">
                                            <div className="spec-tag">{item.garment.size}</div>
                                            <div className="spec-tag category-tag">{item.garment.category.name}</div>
                                        </div>
                                        <div 
                                            className="color-tag" 
                                            style={{ backgroundColor: item.garment.color.hex }}
                                        />
                                    </div>
                                    <div className="cart-item-prices d-flex justify-content-between align-items-center">
                                        <div className="total-price">
                                            {item.total_price} ₽
                                        </div>
                                        <div className="quantity-controls d-flex align-items-center">
                                            <button 
                                                className="quantity-btn btn btn-outline-secondary"
                                                onClick={() => handleUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                                                disabled={item.quantity <= 1}
                                            >
                                                <span className="quantity-btn-icon">−</span>
                                            </button>
                                            <span className="quantity-value mx-2">{item.quantity}</span>
                                            <button 
                                                className="quantity-btn btn btn-outline-secondary"
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                                disabled={item.quantity >= item.garment.count}
                                                title={`На складе: ${item.garment.count} шт.`}
                                            >
                                                <span className="quantity-btn-icon">+</span>
                                            </button>
                                            {item.quantity >= item.garment.count && (
                                                <span className="quantity-warning ms-2">
                                                    На складе осталось: {item.garment.count} шт.
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="cart-summary">
                        <h2>Итого к оплате: {totalSum} ₽</h2>
                        <button 
                            className="checkout-button btn btn-success" 
                            onClick={handleCheckout}
                        >
                            Оформить заказ
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

export default Cart; 