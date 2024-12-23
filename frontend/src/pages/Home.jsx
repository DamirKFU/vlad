import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from '../styles/Home.module.css';
import Preloader from '../components/common/Preloader';

function Home() {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Имитация загрузки
        setTimeout(() => {
            setIsLoading(false);
        }, 1000);
    }, []);

    if (isLoading) {
        return <Preloader message="Загрузка главной страницы..." />;
    }

    return (
        <div className={styles.catalogPage}>
            <div className={styles.heroSection}>
                <h1 className={styles.catalogTitle}>КАТАЛОГ</h1>
                <Link to="/constructor" className={styles.constructorLink}>
                    ПЕРЕЙТИ В КОНСТРУКТОР
                </Link>
            </div>
        </div>
    );
}

export default Home;