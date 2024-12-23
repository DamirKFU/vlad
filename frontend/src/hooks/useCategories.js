import { useState, useEffect } from 'react';
import api from '../api';

const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await fetch("http://localhost:8000/api/catalog/garments/?format=json");
        if (!response.ok) {
          throw new Error("Ошибка при загрузке данных");
        }

        const json = await response.json();

        const structuredData = Object.entries(json).map(([categoryName, categoryData]) => ({
          category: categoryName,
          items: Object.entries(categoryData).map(([size, colors]) => ({
            size,
            details: Object.entries(colors).map(([color, attributes]) => ({
              color,
              hex: attributes.hex,
              id: attributes.id,
              count: attributes.count
            })),
          })),
        }));

        setCategories(structuredData);
      } catch (err) {
        console.error('Error fetching categories:', err);
        setError(err.message || 'Ошибка при загрузке категорий');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, isLoading, error };
};

export default useCategories; 