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

  const handlePhoneChange = (e) => {
    const value = e.target.value;
    
    if (value.length < 2) {
      return;
    }

    const formattedPhone = formatPhoneNumber(value);
    setPhone(formattedPhone);
    
    if (formattedPhone.length === 18 && !validateRussianPhone(formattedPhone)) {
      setPhoneError('Неверный формат номера телефона');
    } else {
      setPhoneError('');
    }
  };

  const handleConfirmOrder = async () => {
    if (!address.trim()) {
      setAddressError('Пожалуйста, ��кажите адрес доставки');
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

    try {
      const response = await api.post('catalog/order/create/', {
        address: address.trim(),
        phone: phone.trim()
      });
      
      if (response.data.success) {
        navigate('/orders');
      }
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Ошибка при создании заказа');
    }
  };

  return (
    <div className="checkout-container">
      <h1>Оформление заказа</h1>
      
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
        >
          Подтвердить заказ
        </button>
      </div>
    </div>
  );
};

export default Checkout; 