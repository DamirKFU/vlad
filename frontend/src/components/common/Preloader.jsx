import React, { useState } from 'react';
import styles from '../../styles/Preloader.module.css';

const Preloader = ({ message = "Загрузка..." }) => {
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
  };

  return (
    isVisible && (
      <div className={`${styles.preloaderContainer}`}>
        <div className={styles.spinner}></div>
        <p className={styles.message}>{message}</p>
        <button onClick={handleClose} className="hidden">Закрыть</button>
      </div>
    )
  );
};

export default Preloader; 