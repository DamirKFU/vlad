import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/Chat.css';

function ChatList() {
    const [chats, setChats] = useState([]);
    const [newChatTopic, setNewChatTopic] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        loadChats();
    }, []);

    const loadChats = async () => {
        try {
            const response = await api.get('support/chats/');
            setChats(response.data.data);
        } catch (error) {
            console.error('Ошибка при загрузке чатов:', error);
        }
    };

    const createChat = async (e) => {
        e.preventDefault();
        if (!newChatTopic.trim()) return;

        try {
            const response = await api.post('support/chats/', {
                topic: newChatTopic
            });
            setNewChatTopic('');
            setIsCreating(false);
            navigate(`/support/${response.data.data.id}`);
        } catch (error) {
            console.error('Ошибка при создании чата:', error);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1 className="chat-title">Чаты поддержки</h1>
                <button
                    onClick={() => setIsCreating(true)}
                    className="new-chat-button"
                >
                    Новый чат
                </button>
            </div>

            {isCreating && (
                <form onSubmit={createChat} className="chat-form">
                    <div className="form-group">
                        <label htmlFor="topic" className="form-label">
                            Тема чата
                        </label>
                        <input
                            type="text"
                            id="topic"
                            value={newChatTopic}
                            onChange={(e) => setNewChatTopic(e.target.value)}
                            className="form-input"
                            placeholder="Введите тему чата..."
                            required
                        />
                        <div className="form-buttons">
                            <button type="submit" className="submit-button">
                                Создать
                            </button>
                            <button
                                type="button"
                                onClick={() => setIsCreating(false)}
                                className="cancel-button"
                            >
                                Отмена
                            </button>
                        </div>
                    </div>
                </form>
            )}

            <div className="chats-table">
                <div className="table-header">
                    <div>ID</div>
                    <div className="col-topic">Тема</div>
                    <div>Дата создания</div>
                    <div>Статус</div>
                </div>

                <div className="chats-list">
                    {chats.map((chat) => (
                        <div
                            key={chat.id}
                            onClick={() => navigate(`/support/${chat.id}`)}
                            className="chat-row"
                        >
                            <div className="chat-id">#{chat.id}</div>
                            <div className="chat-topic">{chat.topic}</div>
                            <div className="chat-date">
                                {new Date(chat.created_at).toLocaleString('ru-RU', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </div>
                            <div>
                                <span className={`chat-status ${chat.is_active ? 'status-active' : 'status-closed'}`}>
                                    {chat.is_active ? 'Активен' : 'Закрыт'}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {chats.length === 0 && (
                <div className="no-chats">
                    У вас пока нет чатов. Создайте новый чат для общения с поддержкой.
                </div>
            )}
        </div>
    );
}

export default ChatList; 