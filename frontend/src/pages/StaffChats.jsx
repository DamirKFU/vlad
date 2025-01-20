import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/StaffChats.css';

function StaffChats() {
    const [chats, setChats] = useState([]);
    const [activeTab, setActiveTab] = useState('my');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        loadChats();
    }, [activeTab]);

    const loadChats = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.get(`staff/support/chats/`, {
                params: {
                    chat_type: activeTab
                }
            });
            setChats(response.data.data.chats);
        } catch (error) {
            setError(error.response?.data?.message || 'Ошибка при загрузке чатов');
        } finally {
            setLoading(false);
        }
    };

    const getTabName = (type) => {
        const names = {
            my: 'Мои чаты',
            unassigned: 'Без ответственного',
            assigned: 'Все активные'
        };
        return names[type];
    };

    const joinChat = async (chatId) => {
        try {
            setLoading(true);
            await api.get(`staff/support/chats/${chatId}/invite/`);
            navigate(`/support/${chatId}`);
        } catch (error) {
            setError(error.response?.data?.message || 'Ошибка при присоединении к чату');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="staff-chats">
            <div className="staff-chats-header">
                <h1>Чаты поддержки</h1>
                <div className="chat-tabs">
                    <button 
                        className={`tab ${activeTab === 'my' ? 'active' : ''}`}
                        onClick={() => setActiveTab('my')}
                    >
                        Мои чаты
                    </button>
                    <button 
                        className={`tab ${activeTab === 'unassigned' ? 'active' : ''}`}
                        onClick={() => setActiveTab('unassigned')}
                    >
                        Без ответственного
                    </button>
                    {localStorage.getItem('isSuperuser') === 'true' && (
                        <button 
                            className={`tab ${activeTab === 'assigned' ? 'active' : ''}`}
                            onClick={() => setActiveTab('assigned')}
                        >
                            Все активные
                        </button>
                    )}
                </div>
            </div>

            {loading && (
                <div className="loading">Загрузка чатов...</div>
            )}

            {error && (
                <div className="error">{error}</div>
            )}

            <div className="chats-grid">
                {chats.map((chat) => (
                    <div 
                        key={chat.id} 
                        className="chat-card"
                        onClick={() => navigate(`/support/${chat.id}`)}
                    >
                        <div className="chat-card-header">
                            <span className="chat-id">#{chat.id}</span>
                            <span className={`chat-status ${chat.is_active ? 'active' : 'closed'}`}>
                                {chat.is_active ? 'Активен' : 'Закрыт'}
                            </span>
                        </div>
                        <h3 className="chat-topic">{chat.topic}</h3>
                        <div className="chat-info">
                            <div className="chat-user">
                                <span className="label">Пользователь:</span>
                                <span>{chat.user.username}</span>
                            </div>
                            <div className="chat-date">
                                <span className="label">Создан:</span>
                                <span>
                                    {new Date(chat.created_at).toLocaleString('ru-RU', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </span>
                            </div>
                            {chat.responsible_users.length > 0 && (
                                <div className="chat-responsible">
                                    <span className="label">Ответственные:</span>
                                    <div className="responsible-list">
                                        {chat.responsible_users.map(user => (
                                            <span key={user.id} className="responsible-user">
                                                {user.username}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className="chat-actions">
                            {activeTab === 'unassigned' ? (
                                <button 
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        joinChat(chat.id);
                                    }}
                                    className="join-button"
                                >
                                    Присоединиться к чату
                                </button>
                            ) : (
                                <button 
                                    onClick={() => navigate(`/support/${chat.id}`)}
                                    className="open-chat-button"
                                >
                                    Открыть чат
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {!loading && !error && chats.length === 0 && (
                <div className="no-chats">
                    {`${getTabName(activeTab)} отсутствуют`}
                </div>
            )}
        </div>
    );
}

export default StaffChats; 