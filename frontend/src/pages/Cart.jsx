import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/Cart.css';

const Cart = () => {
    const [cartItems, setCartItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
            await api.patch(`catalog/cart/item/${itemId}/`, {
                quantity: newQuantity
            });
            fetchCart(); // Обновляем корзину после изменения количества
        } catch (err) {
            console.error('Ошибка при обновлении количества:', err);
        }
    };

    const handleRemoveItem = async (itemId) => {
        try {
            await api.delete('catalog/cart/', {
                data: { item_id: itemId }
            });
            fetchCart(); // Обновляем корзину после удаления
        } catch (err) {
            console.error('Ошибка при удалении товара:', err);
        }
    };

    if (loading) return <p>Загрузка...</p>;
    if (error) return <p>{error}</p>;

    const totalSum = cartItems.reduce((sum, item) => sum + item.total_price, 0);

    return (
        <div className="cart">
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
                                <div className="cart-item-info">
                                    <h3>{item.name}</h3>
                                    <p>Размер: {item.size}</p>
                                    <p>Цвет: {item.color}</p>
                                    <p>Цена: {item.price} руб</p>
                                    <div className="quantity-controls">
                                        <button 
                                            onClick={() => handleUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                                            disabled={item.quantity <= 1}
                                        >
                                            -
                                        </button>
                                        <span>{item.quantity}</span>
                                        <button 
                                            onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                        >
                                            +
                                        </button>
                                    </div>
                                    <p>Итого: {item.total_price} руб</p>
                                    <button 
                                        className="remove-button"
                                        onClick={() => handleRemoveItem(item.id)}
                                    >
                                        Удалить
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="cart-summary">
                        <h2>Итого к оплате: {totalSum} руб</h2>
                        <button className="checkout-button">Оформить заказ</button>
                    </div>
                </>
            )}
        </div>
    );
};

export default Cart; 