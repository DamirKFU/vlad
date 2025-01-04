import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../api';

const TelegramAuth = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = searchParams.get('token');
        if (!token) {
            setError('Отсутствует токен авторизации');
            return;
        }

        const authTelegram = async () => {
            try {
                const response = await api.post('telegram-bot/auth/', {
                    token: token
                });
                navigate('/', { 
                    state: { message: response.data.message }
                });
            } catch (err) {
                setError(err.response?.data?.errors?.form_error || 'Ошибка привязки Telegram');
                if (err.response?.status === 403) {
                    navigate('/login', { 
                        state: { redirectTo: window.location.pathname + window.location.search }
                    });
                }
            }
        };

        authTelegram();
    }, [searchParams, navigate]);

    if (error) {
        return (
            <div className="container">
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="container">
            <div className="text-center">
                <div className="spinner-border" role="status">
                    <span className="visually-hidden">Загрузка...</span>
                </div>
                <p>Подключение Telegram...</p>
            </div>
        </div>
    );
};

export default TelegramAuth; 