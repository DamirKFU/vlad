import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/Cart.css';
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
            setCartItems(response.data);
            setLoading(false);
        } catch (err) {
            setError('Ошибка при загрузке корзины');
            setLoading(false);
        }
    };

    const handleUpdateQuantity = async (itemId, newQuantity) => {
        try {
            const response = await api.patch(`catalog/cart/item/${itemId}/`, {
                quantity: newQuantity
            });
            
            // Обновляем только измененный элемент
            setCartItems(prevItems => 
                prevItems.map(item => 
                    item.id === itemId 
                        ? { ...item, quantity: response.data.quantity, total_price: response.data.total_price }
                        : item
                )
            );
        } catch (err) {
            console.error('Ошибка при обновлении количества:', err);
        }
    };

    const handleRemoveItem = async (itemId) => {
        try {
            await api.delete(`catalog/cart/item/${itemId}/`);
            // Удаляем элемент из состояния
            setCartItems(prevItems => prevItems.filter(item => item.id !== itemId));
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
                            <div key={item.id} className="cart-item">
                                <div className="cart-item-image">
                                    <img src={item.image} alt={item.name} />
                                </div>
                                <div className="cart-item-details">
                                    <div className="cart-item-header">
                                        <h3>{item.name}</h3>
                                        <button 
                                            className="remove-button"
                                            onClick={() => handleRemoveItem(item.id)}
                                            aria-label="Удалить товар"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                    <div className="cart-item-specs">
                                        <div className="spec-group">
                                            <div className="spec-tag">{item.size}</div>
                                            <div className="spec-tag category-tag">{item.category}</div>
                                        </div>
                                        <div 
                                            className="color-tag" 
                                            style={{ backgroundColor: item.color }}
                                        />
                                    </div>
                                    <div className="cart-item-prices">
                                        <div className="total-price">
                                            {item.total_price} ₽
                                        </div>
                                        <div className="quantity-controls">
                                            <button 
                                                className="quantity-btn"
                                                onClick={() => handleUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                                                disabled={item.quantity <= 1}
                                            >
                                                <span className="quantity-btn-icon">−</span>
                                            </button>
                                            <span className="quantity-value">{item.quantity}</span>
                                            <button 
                                                className="quantity-btn"
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                                disabled={item.quantity >= item.available_quantity}
                                                title={`На складе: ${item.available_quantity} шт.`}
                                            >
                                                <span className="quantity-btn-icon">+</span>
                                            </button>
                                            {item.quantity >= item.available_quantity && (
                                                <span className="quantity-warning">
                                                    На складе остал��сь: {item.available_quantity} шт.
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
                            className="checkout-button" 
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