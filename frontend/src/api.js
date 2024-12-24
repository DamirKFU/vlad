import axios from "axios";
import Cookies from 'js-cookie';


const api = axios.create({
    baseURL: "http://localhost:8000/api/",
    withCredentials: true
});

api.interceptors.request.use(
    async (config) => {
        const csrf_token = Cookies.get('csrftoken');
        if (!csrf_token) {
            try {
                await axios.get('http://localhost:8000/api/get-csrf-token/', { withCredentials: true });
                config.headers['X-CSRFToken'] = Cookies.get('csrftoken');
            } catch (error) {
                return Promise.reject(error);
            }
        } else {
            config.headers['X-CSRFToken'] = csrf_token;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 403) {
            // Перенаправление на страницу логина
            window.location.href = '/login'; // Замените '/login' на ваш путь к странице логина
        }
        return Promise.reject(error);
    }
);

export default api;
