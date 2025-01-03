import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api';
import { validateRussianPhone, formatPhoneNumber } from '../utils/validators';
import '../styles/Checkout.css';

const Checkout = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { cartItems = [], totalSum = 0 } = location.state || {};
    const [address, setAddress] = useState('');
    const [addressError, setAddressError] = useState('');
    const [phone, setPhone] = useState('+7');
    const [phoneError, setPhoneError] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [loadingMessage, setLoadingMessage] = useState('');

    const handlePhoneChange = (e) => {
        const value = e.target.value;
        if (value.length < 2) return;
        
        const formattedPhone = formatPhoneNumber(value);
        setPhone(formattedPhone);
        
        if (formattedPhone.length === 18 && !validateRussianPhone(formattedPhone)) {
            setPhoneError('Неверный формат номера телефона');
        } else {
            setPhoneError('');
        }
    };

    const checkTaskStatus = async (taskId) => {
        try {
            const response = await api.get(`core/task/${taskId}/`);
            const { message, data } = response.data;

            // Если задача еще выполняется
            if (message === 'Задача еще не выполнена') {
                return false;
            }

            // Если задача выполнена успешно
            if (data?.order_id) {
                navigate(`/orders/${data.order_id}`);
                return true;
            }

            // Обработка ошибок валидации и других ошибок
            if (data?.errors) {
                if (data.errors.form_error) {
                    setError(data.errors.form_error);
                } else {
                    if (data.errors.address) {
                        setAddressError(data.errors.address[0]);
                    }
                    if (data.errors.phone) {
                        setPhoneError(data.errors.phone[0]);
                    }
                }
                setLoading(false);
                return true;
            }

            return false;

        } catch (err) {
            if (err.response?.status === 404) {
                setError('Не удалось создать заказ: задача не найдена');
                setLoading(false);
                return true;
            }
            // Добавляем обработку 400 статуса
            if (err.response?.status === 400) {
                const { errors, message } = err.response.data;
                if (errors?.form_error) {
                    setError(errors.form_error);
                } else if (errors) {
                    if (errors.address) {
                        setAddressError(errors.address[0]);
                    }
                    if (errors.phone) {
                        setPhoneError(errors.phone[0]);
                    }
                } else {
                    setError(message || 'Ошибка валидации');
                }
                setLoading(false);
                return true;
            }
            return false;
        }
    };

    const pollTaskStatus = async (taskId) => {
        let attempts = 0;
        const maxAttempts = 30;
        const interval = 2000;

        while (attempts < maxAttempts) {
            const isCompleted = await checkTaskStatus(taskId);
            if (isCompleted) return;
            await new Promise(resolve => setTimeout(resolve, interval));
            attempts++;
        }

        setError('Превышено время ожидания создания заказа');
        setLoading(false);
    };

    const handleConfirmOrder = async () => {
        if (!address.trim()) {
            setAddressError('Пожалуйста, укажите адрес доставки');
            return;
        }

        if (phone.length < 18) {
            setPhoneError('Пожалуйста, введите полный номер телефона');
            return;
        }

        if (!validateRussianPhone(phone)) {
            setPhoneError('Неверный формат номера телефона');
            return;
        }

        setLoading(true);
        setLoadingMessage('Пожалуйста, подождите. Мы создаем ваш заказ и подготавливаем платежную информацию...');
        setError(null);

        try {
            const response = await api.post('catalog/order/create/', {
                address: address.trim(),
                phone: phone.trim()
            });
            
            const taskId = response.data.data.task_id;
            setLoadingMessage('Проверяем статус заказа...');
            pollTaskStatus(taskId);

        } catch (err) {
            setError(err.response?.data?.errors?.form_error 
                || err.response?.data?.message 
                || 'Ошибка при создании заказа');
            setLoading(false);
            setLoadingMessage('');
        }
    };

    return (
        <div className="checkout-container">
            <h1>Оформление заказа</h1>
            
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {loading && loadingMessage && (
                <div className="loading-message">
                    <div className="loading-spinner"></div>
                    <p>{loadingMessage}</p>
                </div>
            )}

            <div className="checkout-items">
                {cartItems.map(item => (
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
                <h2>Адрес доставки</h2>
                <div className="address-input-container">
                    <input
                        type="text"
                        className={`address-input ${addressError ? 'error' : ''}`}
                        placeholder="Введите адрес доставки"
                        value={address}
                        onChange={(e) => {
                            setAddress(e.target.value);
                            setAddressError('');
                        }}
                        disabled={loading}
                    />
                    {addressError && (
                        <div className="address-error">
                            {addressError}
                        </div>
                    )}
                </div>
                <p className="delivery-info">
                    Доставка осуществляется только в пределах города
                </p>
            </div>

            <div className="delivery-section">
                <h2>Телефон</h2>
                <div className="phone-input-container">
                    <input
                        type="tel"
                        className={`phone-input ${phoneError ? 'error' : ''}`}
                        placeholder="+7 (999) 123-45-67"
                        value={phone}
                        onChange={handlePhoneChange}
                        disabled={loading}
                    />
                    {phoneError && (
                        <div className="phone-error">
                            {phoneError}
                        </div>
                    )}
                </div>
                <p className="phone-info">
                    Введите номер в формате: +7 (999) 123-45-67
                </p>
            </div>

            <div className="checkout-summary">
                <div className="total-info">
                    <h2>Итого к оплате:</h2>
                    <span className="total-price">{totalSum} ₽</span>
                </div>
                <button 
                    className="confirm-order-btn"
                    onClick={handleConfirmOrder}
                    disabled={loading}
                >
                    {loading ? 'Создание заказа...' : 'Подтвердить заказ'}
                </button>
            </div>
        </div>
    );
};

export default Checkout; 