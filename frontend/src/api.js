import axios from "axios";
import Cookies from 'js-cookie';
import { API_URL } from './constants/core';


const api = axios.create({
    baseURL: `${API_URL}/api/`,
    withCredentials: true
});

api.interceptors.request.use(
    async (config) => {
        const csrf_token = Cookies.get('csrftoken');
        if (!csrf_token) {
            try {
                await axios.get(`${API_URL}/api/get-csrf-token/`, { withCredentials: true });
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


export default api;
