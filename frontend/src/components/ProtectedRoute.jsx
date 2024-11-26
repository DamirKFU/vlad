import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import React, { useState, useEffect, useCallback } from "react";
import Cookies from 'js-cookie';

const ProtectedRoute = React.memo(({ children }) => {
    const [isAuthorized, setIsAuthorized] = useState(null);
    const refreshToken = useCallback(async () => {
        const refreshToken = Cookies.get(REFRESH_TOKEN);
        try {
            const res = await api.post("/token/refresh/", {
                refresh: refreshToken,
            }, { withCredentials: true });
            if (res.status === 200) {
                setIsAuthorized(true);
            } else {
                setIsAuthorized(false);
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    }, []);

    const auth = useCallback(async () => {
        const token = Cookies.get(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        const decoded = jwtDecode(token);
        const tokenExpiration = decoded.exp;
        const now = Date.now() / 1000;

        if (tokenExpiration < now) {
            await refreshToken();
        } else {
            setIsAuthorized(true);
        }
    }, [refreshToken]);

    useEffect(() => {
        auth().catch(() => setIsAuthorized(false))
    }, [auth])

    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
})

export default ProtectedRoute;