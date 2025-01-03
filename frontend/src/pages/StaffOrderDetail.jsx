import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/StaffOrderDetail.css';
import OrderLogs from '../components/OrderLogs';

const ReturnForm = ({
    returnComment,
    setReturnComment,
    onCancel,
    onSubmit
}) => (
    <div className="return-form">
        <h3>Укажите причину возврата</h3>
        <textarea
            value={returnComment}
            onChange={(e) => setReturnComment(e.target.value)}
            placeholder="Опишите причину возврата заказа"
            className="return-comment"
        />
        <div className="button-group">
            <button
                className="cancel-button"
                onClick={onCancel}
            >
                Отмена
            </button>
            <button
                className="return-button"
                onClick={onSubmit}
                disabled={!returnComment.trim()}
            >
                Подтвердить возврат
            </button>
        </div>
    </div>
);

const getReturnButtonText = (status) => {
    switch (status) {
        case 'IW': // IN_WORK
            return 'Вернуть в разработку';
        case 'DR': // DRAFT
            return 'Вернуть на пошив';
        case 'ID': // IN_DELIVERY
            return 'Вернуть на сборку';
        default:
            return 'Вернуть';
    }
};

const StaffOrderDetail = (props) => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [trackingCode, setTrackingCode] = useState('');
    const [returnComment, setReturnComment] = useState('');
    const [showReturnForm, setShowReturnForm] = useState(false);
    const [embroideries, setEmbroideries] = useState({});

    useEffect(() => {
        fetchOrderDetails();
    }, [orderId]);

    const fetchOrderDetails = async () => {
        try {
            const response = await api.get(`staff/orders/${orderId}/`);
            setOrder(response.data.data);
            if (response.data.data.tracking_code) {
                setTrackingCode(response.data.data.tracking_code);
            }
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.message || 'Ошибка при загрузке заказа');
            setLoading(false);
        }
    };

    const handleTrackingCodeSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post(`staff/orders/${orderId}/`, {
                tracking_code: trackingCode
            });
            fetchOrderDetails();
        } catch (err) {
            const errorMessage = err.response?.data?.serializer_errors
                ? Object.values(err.response.data.serializer_errors)[0][0]
                : err.response?.data?.message || 'Ошибка при обновлении кода отслеживания';
            setError(errorMessage);
        }
    };

    const handleDownload = async (path) => {
        try {
            const response = await api.get('core/download/', {
                params: { path },
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', path.split('/').pop());
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            setError('Ошибка при скачивании файла');
        }
    };

    const handleComplete = async () => {
        try {
            const data = order.status === 'DR' ? { tracking_code: trackingCode } : {};
            await api.post(`staff/orders/${orderId}/`, data);
            fetchOrderDetails();
        } catch (err) {
            const errorMessage = err.response?.data?.serializer_errors
                ? Object.values(err.response.data.serializer_errors)[0][0]
                : err.response?.data?.message || 'Ошибка при обновлении статуса';
            setError(errorMessage);
        }
    };

    const handleReturn = async () => {
        if (!returnComment.trim()) {
            setError('Необходимо указать причину возврата');
            return;
        }

        try {
            await api.delete(`staff/orders/${orderId}/`, {
                data: { error_comment: returnComment }
            });
            setShowReturnForm(false);
            setReturnComment('');
            fetchOrderDetails();
        } catch (err) {
            const errorMessage = err.response?.data?.serializer_errors
                ? Object.values(err.response.data.serializer_errors)[0][0]
                : err.response?.data?.message || 'Ошибка при возврате заказа';
            setError(errorMessage);
        }
    };

    const handleFileSelect = (itemId, category, file) => {
        setEmbroideries(prev => ({
            ...prev,
            [itemId]: {
                file,
                category: parseInt(category)
            }
        }));
    };

    const handleStartSewing = async () => {
        try {
            const items = order.items.map((item, index) => {
                return {
                    id: item.id,
                    product_id: item.product_id,
                    category_id: item.category_id,
                    embroidery: null,
                };
            });

            const formData = new FormData();
            formData.append('items', JSON.stringify(items));
            console.log(embroideries)
            items.forEach((item, index) => {
                if (embroideries[item.id]) {
                    formData.append(`embroidery_${item.id}`, embroideries[item.id].file);
                }
            });

            await api.post(`staff/orders/${orderId}/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            fetchOrderDetails();
        } catch (err) {
            console.error(err);
            const errorMessage = err.response?.data?.serializer_errors
                ? Object.values(err.response.data.serializer_errors)[0][0]
                : err.response?.data?.message || 'Ошибка при загрузке вышивок';
            setError(errorMessage);
        }
    };

    const renderOrderContent = () => {
        switch (order.status) {
            case 'IW': // IN_WORK
                return (
                    <div className="order-items">
                        {order.items.map((item) => (
                            <div key={item.id} className="order-item">
                                <div className="item-images">
                                    <div className="image-container">
                                        <h4>Изображение</h4>
                                        {item.image && (
                                            <img src={item.image} alt="Изображение товара" />
                                        )}
                                    </div>
                                    <div className="image-container">
                                        <h4>Вышивка</h4>
                                        {item.embroidery && (
                                            <button
                                                className="download-button"
                                                onClick={() => handleDownload(item.embroidery)}
                                            >
                                                Скачать
                                            </button>
                                        )}
                                    </div>
                                </div>
                                <div className="item-details">
                                    <p><strong>Размер:</strong> {item.size}</p>
                                    <p><strong>Цвет:</strong> {item.color}</p>
                                    <p><strong>Количество:</strong> {item.quantity}</p>
                                </div>
                            </div>
                        ))}
                        <div className="button-group">
                            <button
                                className="action-button return-button"
                                onClick={() => setShowReturnForm(true)}
                            >
                                {getReturnButtonText(order.status)}
                            </button>
                            <button
                                className="action-button complete-button"
                                onClick={handleComplete}
                            >
                                Завершить пошив
                            </button>
                        </div>
                    </div>
                );

            case 'DR': // DRAFT
                return (
                    <div className="tracking-code-section">
                        <div className="form-group">
                            <label>Код отслеживания:</label>
                            <input
                                type="text"
                                value={trackingCode}
                                onChange={(e) => setTrackingCode(e.target.value)}
                                placeholder="Введите код отслеживания"
                            />
                        </div>
                        <div className="button-group">
                            <button
                                className="action-button return-button"
                                onClick={() => setShowReturnForm(true)}
                            >
                                {getReturnButtonText(order.status)}
                            </button>
                            <button
                                className="action-button complete-button"
                                onClick={() => handleComplete()}
                                disabled={!trackingCode}
                            >
                                Отправить в доставку
                            </button>
                        </div>
                    </div>
                );

            case 'PD': // PAID
                return (
                    <div className="order-items">
                        {order.items.map((item) => (
                            <div key={item.id} className="order-item">
                                <div className="item-images">
                                    <div className="image-container">
                                        <h4>Изображение</h4>
                                        {item.image && (
                                            <img src={item.image} alt="Изображение товара" />
                                        )}
                                    </div>
                                    <div className="image-container">
                                        <h4>Вышивка</h4>
                                        {item.embroidery && (
                                            <button
                                                className="download-button"
                                                onClick={() => handleDownload(item.embroidery)}
                                            >
                                                Скачать
                                            </button>
                                        )}
                                        {embroideries[item.id] ? (
                                            <div className="file-selected">
                                                <span>{embroideries[item.id].file.name}</span>
                                                <button
                                                    className="remove-file"
                                                    onClick={() => {
                                                        setEmbroideries(prev => {
                                                            const newState = { ...prev };
                                                            delete newState[item.id];
                                                            return newState;
                                                        });
                                                    }}
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="upload-container">
                                                <input
                                                    type="file"
                                                    id={`file-input-${item.id}`}
                                                    onChange={(e) => handleFileSelect(
                                                        item.id,
                                                        item.category_id,
                                                        e.target.files[0]
                                                    )}
                                                    accept=".dst"
                                                    className="file-input"
                                                />
                                                <label
                                                    htmlFor={`file-input-${item.id}`}
                                                    className="upload-button"
                                                >
                                                    Загрузить вышивку
                                                </label>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="item-details">
                                    <p><strong>Размер:</strong> {item.size}</p>
                                    <p><strong>Категория:</strong> {item.category}</p>
                                </div>
                            </div>
                        ))}
                        <div className="button-group">
                            <button
                                className="action-button complete-button"
                                onClick={handleStartSewing}
                                disabled={!order.items.every(item =>
                                    item.embroidery || embroideries[item.id]
                                )}
                            >
                                Начать пошив
                            </button>
                        </div>
                    </div>
                );

            case 'ID': // IN_DELIVERY
                return (
                    <div className="order-actions">
                        <div className="tracking-info">
                            <label>Код отслеживания:</label>
                            <div className="tracking-code">{order.tracking_code}</div>
                        </div>
                        <div className="button-group">
                            <button
                                className="action-button return-button"
                                onClick={() => setShowReturnForm(true)}
                            >
                                {getReturnButtonText(order.status)}
                            </button>
                            <button
                                className="action-button complete-button"
                                onClick={handleComplete}
                            >
                                Подтвердить доставку
                            </button>
                        </div>
                    </div>
                );

            default:
                return <p>Нет доступных действий</p>;
        }
    };

    if (loading) return <div className="loading">Загрузка...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!order) return <div className="error">Заказ не найден</div>;

    return (
        <div className={`staff-order-detail ${showReturnForm ? 'show-overlay' : ''}`}>
            <div className="order-header">
                <h1>Заказ #{order.id}</h1>
                <div className={`order-status ${order.status.toLowerCase()}`}>
                    {order.status_display}
                </div>
            </div>
            {order.last_log && (
                <div className="last-error">
                    <div className="error-header">
                        <span className="error-user">{order.last_log.user}</span>
                        <span className="error-date">
                            {new Date(order.last_log.created_at).toLocaleString()}
                        </span>
                    </div>
                    {order.last_log.comment && (
                        <div className="error-comment">
                            {order.last_log.comment}
                        </div>
                    )}
                </div>
            )}
            {renderOrderContent()}
            {showReturnForm && (
                <ReturnForm
                    returnComment={returnComment}
                    setReturnComment={setReturnComment}
                    onCancel={() => {
                        setShowReturnForm(false);
                        setReturnComment('');
                    }}
                    onSubmit={handleReturn}
                />
            )}
            <OrderLogs orderId={orderId} />
        </div>
    );
};

export default StaffOrderDetail;
