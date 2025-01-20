import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import Cookies from 'js-cookie';
import api from '../api';
import '../styles/Chat.css';

function Support() {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const [userData, setUserData] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [showUserSearch, setShowUserSearch] = useState(false);
    const { chatId } = useParams();
    const messagesEndRef = useRef(null);

    useEffect(() => {
        const csrftoken = Cookies.get('csrftoken');
        const ws = new WebSocket(`ws://localhost:8000/ws/support/chat/${chatId}/`, ['X-CSRFToken', csrftoken]);

        ws.onopen = () => {
            console.log('WebSocket соединение установлено');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Получено сообщение:', data);

            if (data.type === 'chat_message') {
                setMessages(prev => [...prev, data.message]);
                messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            } else if (data.type === 'chat_history') {
                setMessages(data.messages);
                setUserData(data.user);
                messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket ошибка:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket соединение закрыто');
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, [chatId]);

    const searchUsers = async (query) => {
        if (query.length < 2) {
            setSearchResults([]);
            return;
        }

        try {
            const response = await api.get(`users/search/?query=${query}`);
            setSearchResults(response.data.data);
        } catch (error) {
            console.error('Ошибка при поиске пользователей:', error);
        }
    };

    const addUser = async (userId) => {
        try {
            await api.post(`staff/support/chats/${chatId}/invite/`, {
                user_id: userId
            });
            setShowUserSearch(false);
            setSearchQuery('');
            setSearchResults([]);
        } catch (error) {
            console.error('Ошибка при добавлении пользователя:', error);
        }
    };

    const sendMessage = (e) => {
        e.preventDefault();
        if (message.trim() && socket) {
            socket.send(JSON.stringify({
                type: 'chat_message',
                message: message
            }));
            setMessage('');
        }
    };

    return (
        <div className="chat-window">
            {userData?.is_staff && (
                <div className="chat-header">
                    <button 
                        onClick={() => setShowUserSearch(true)}
                        className="add-user-button"
                    >
                        Добавить ответственного
                    </button>
                </div>
            )}

            <div className="chat-messages">
                {messages.map((msg) => (
                    <div 
                        key={msg.id} 
                        className={`message ${msg.user_id === userData?.user_id ? 'outgoing' : 'incoming'} ${
                            msg.is_system ? 'system' : ''
                        }`}
                    >
                        <div className="message-header">
                            <span className="message-username">{msg.username}</span>
                            <span className="message-time">
                                {new Date(msg.created_at).toLocaleString('ru-RU', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </span>
                        </div>
                        <div className="message-content">{msg.content}</div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            
            <div className="chat-input-container">
                <form onSubmit={sendMessage} className="chat-input-form">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        className="chat-input"
                        placeholder="Введите сообщение..."
                    />
                    <button
                        type="submit"
                        className="send-button"
                        disabled={!message.trim()}
                    >
                        Отправить
                    </button>
                </form>
            </div>

            {showUserSearch && (
                <div className="user-search-modal">
                    <div className="modal-content">
                        <h3>Добавить ответственного</h3>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                searchUsers(e.target.value);
                            }}
                            placeholder="Введите имя пользователя..."
                            className="search-input"
                        />
                        <div className="search-results">
                            {searchResults.map(user => (
                                <div 
                                    key={user.id}
                                    className="user-result"
                                    onClick={() => addUser(user.id)}
                                >
                                    {user.username}
                                </div>
                            ))}
                        </div>
                        <button 
                            onClick={() => {
                                setShowUserSearch(false);
                                setSearchQuery('');
                                setSearchResults([]);
                            }}
                            className="close-button"
                        >
                            Закрыть
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Support; 