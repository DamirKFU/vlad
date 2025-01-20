import React from 'react';
import Navbar from '../components/Navbar';
import '../styles/Home.css'; // Убедитесь, что этот путь правильный
import '../styles/bootstrap-5.3.3-dist/css/bootstrap.min.css'

const Home = () => {
    return (
        <div>
            <Navbar />
            <div className="home-content">
                <h1>Добро пожаловать в MyApp!</h1>
                <p>Это главная страница вашего приложения.</p>
            </div>
        </div>
    );
};

export default Home;