import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/StaffOrders.css';

const ORDER_STATUSES = {
    WP: { label: 'Ожидает оплаты', className: 'waiting-payment' },
    PD: { label: 'В разработке', className: 'in-development' },
    IW: { label: 'На шитье', className: 'in-work' },
    DR: { label: 'На сборке', className: 'draft' },
    ID: { label: 'В доставке', className: 'in-delivery' },
    DV: { label: 'Доставлен', className: 'delivered' },
    CN: { label: 'Отменён', className: 'canceled' }
};

const StaffOrders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [currentStatus, setCurrentStatus] = useState('PD');
    const [allowedStatuses, setAllowedStatuses] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchOrders(currentPage);
    }, [currentPage, currentStatus]);

    const fetchOrders = async (page) => {
        try {
            const response = await api.get(`staff/orders/?status=${currentStatus}&page=${page}`);
            const { results, count, allowed_statuses } = response.data.data;
            setOrders(results);
            setTotalPages(Math.ceil(count / 10));
            setAllowedStatuses(allowed_statuses);

            // Если текущий статус не разрешен, переключаемся на первый разрешенный
            if (allowed_statuses.length > 0 && !allowed_statuses.includes(currentStatus)) {
                setCurrentStatus(allowed_statuses[0]);
            }
            
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.message || 'Ошибка при загрузке заказов');
            setLoading(false);
        }
    };

    const getStatusInfo = (status) => {
        return ORDER_STATUSES[status] || { label: status, className: '' };
    };

    const handleStatusChange = (status) => {
        setCurrentStatus(status);
        setCurrentPage(1);
    };

    const handleOrderClick = (orderId) => {
        navigate(`/staff/orders/${orderId}`);
    };

    if (loading) return <div className="staff-orders-loading">Загрузка заказов...</div>;
    if (error) return <div className="staff-orders-error">{error}</div>;

    return (
        <div className="staff-orders-container">
            <h1>Управление заказами</h1>

            <div className="status-tabs">
                {allowedStatuses.map(status => (
                    <button
                        key={status}
                        className={`status-tab ${getStatusInfo(status).className} ${currentStatus === status ? 'active' : ''}`}
                        onClick={() => handleStatusChange(status)}
                    >
                        {getStatusInfo(status).label}
                    </button>
                ))}
            </div>
            
            <div className="orders-grid">
                {orders.map(order => (
                    <div 
                        key={order.id} 
                        className="order-row"
                        onClick={() => handleOrderClick(order.id)}
                    >
                        <div className="order-title">Заказ №{order.id}</div>
                        <div className={`order-status ${getStatusInfo(order.status.status).className}`}>
                            {order.status.status_display}
                        </div>
                    </div>
                ))}
                {orders.length === 0 && (
                    <div className="no-orders">Нет заказов в данной категории</div>
                )}
            </div>

            {totalPages > 1 && (
                <div className="pagination">
                    <button 
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={currentPage === 1}
                    >
                        Предыдущая
                    </button>
                    <span>Страница {currentPage} из {totalPages}</span>
                    <button 
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={currentPage === totalPages}
                    >
                        Следующая
                    </button>
                </div>
            )}
        </div>
    );
};

export default StaffOrders; 