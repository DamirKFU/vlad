import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/OrderLogs.css';

const OrderLogs = ({ orderId }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        count: 0,
        next: false,
        previous: false,
        current: 1,
        total_pages: 1
    });

    const fetchLogs = async (page = 1) => {
        try {
            const response = await api.get(`staff/orders/${orderId}/logs/`, {
                params: { page }
            });
            const { results, count, next, previous, total_pages } = response.data.data;
            setLogs(results);
            setPagination({
                count,
                next,
                previous,
                current: page,
                total_pages
            });
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.message || 'Ошибка при загрузке логов');
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, [orderId]);

    const handlePageChange = (page) => {
        fetchLogs(page);
    };

    if (loading) return <div className="logs-loading">Загрузка истории...</div>;
    if (error) return <div className="logs-error">{error}</div>;

    return (
        <div className="order-logs">
            <h3>История изменений</h3>
            <div className="logs-list">
                {logs.map((log, index) => (
                    <div key={index} className="log-item">
                        <div className="log-header">
                            <span className="log-user">{log.username}</span>
                            <span className="log-date">
                                {new Date(log.created_at).toLocaleString()}
                            </span>
                        </div>
                        <div className="log-status-change">
                            {log.from_status} → {log.to_status}
                        </div>
                        {log.error_comment && (
                            <div className="log-comment">
                                {log.error_comment}
                            </div>
                        )}
                    </div>
                ))}
                {logs.length === 0 && (
                    <div className="no-logs">История изменений пуста</div>
                )}
            </div>
            {pagination.count > 0 && (
                <div className="pagination">
                    <button
                        className="pagination-button"
                        onClick={() => handlePageChange(pagination.current - 1)}
                        disabled={!pagination.previous}
                    >
                        Назад
                    </button>
                    <span className="pagination-info">
                        Страница {pagination.current} из {pagination.total_pages}
                    </span>
                    <button
                        className="pagination-button"
                        onClick={() => handlePageChange(pagination.current + 1)}
                        disabled={!pagination.next}
                    >
                        Вперед
                    </button>
                </div>
            )}
        </div>
    );
};

export default OrderLogs; 