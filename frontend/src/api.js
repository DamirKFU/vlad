import axios from "axios"
import { ACCESS_TOKEN, CSRF_TOKEN } from "./constants"
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: "http://localhost:8000/api/"
})

api.interceptors.request.use(
    async (config) => {
        const token = Cookies.get(ACCESS_TOKEN);
        const csrf_token = Cookies.get(CSRF_TOKEN);
        if (!csrf_token) {
            try {
                await axios.get('http://localhost:8000/api/get-csrf-token/', { withCredentials: true });
                config.headers['X-CSRFToken'] = Cookies.get(CSRF_TOKEN);
            } catch (error) {
                return Promise.reject(error);
            }
        }
        else {
            config.headers['X-CSRFToken'] = csrf_token;
        }
        if (token){
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default api
