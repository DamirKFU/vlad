import axios from "axios"
import { ACCESS_TOKEN } from "./constants"
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: "http://localhost:8000/"
})

api.interceptors.request.use(
    (config) => {
        const token = Cookies.get(ACCESS_TOKEN);
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
