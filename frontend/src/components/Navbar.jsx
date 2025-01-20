import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Navbar.css'; // Убедитесь, что этот путь правильный

const Navbar = () => {
    const location = useLocation();

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
            <div className="container-fluid">
                <Link className="navbar-brand" to="/">MyApp</Link>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav">
                        <li className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
                            <Link className="nav-link" to="/">Главная</Link>
                        </li>
                        <li className={`nav-item ${location.pathname === '/catalog' ? 'active' : ''}`}>
                            <Link className="nav-link" to="/catalog">Каталог</Link>
                        </li>
                        <li className={`nav-item ${location.pathname === '/support' ? 'active' : ''}`}>
                            <Link className="nav-link" to="/support">Поддержка</Link>
                        </li>
                        <li className={`nav-item ${location.pathname === '/staff' ? 'active' : ''}`}>
                            <Link className="nav-link" to="/staff">Чаты поддержки</Link>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
};

export default Navbar; 