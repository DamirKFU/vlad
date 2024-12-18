import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../styles/Home.module.css';

function Home() {
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