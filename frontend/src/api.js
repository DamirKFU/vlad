import axios from "axios"
import { ACCESS_TOKEN, CSRF_TOKEN } from "./constants"
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: "http://localhost:8000/api/"
})

fetch('http://localhost:8000/api/get-csrf-token/', {
    method: 'GET',
    credentials: 'include'
})

api.interceptors.request.use(
    (config) => {
        const token = Cookies.get(ACCESS_TOKEN);
        const csrf_token = Cookies.get(CSRF_TOKEN);
        if (token){
            config.headers.Authorization = `Bearer ${token}`
        }
        if (csrf_token){
            config.headers['X-CSRFToken'] = csrf_token
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default api
