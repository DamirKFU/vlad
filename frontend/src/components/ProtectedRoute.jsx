import { Navigate } from "react-router-dom";
import api from "../api";
import React, { useState, useEffect, useCallback } from "react";

const ProtectedRoute = React.memo(({ children }) => {
    const [isAuthorized, setIsAuthorized] = useState(null);

    const auth = useCallback(async () => {
        const res = await api.post("/users/is_auth/", {}, { withCredentials: true });
        if (res.status === 200) {
            setIsAuthorized(true);
        } else {
            setIsAuthorized(false);
        }
    }, []);

    useEffect(() => {
        auth().catch(() => setIsAuthorized(false))
    }, [auth])
    
    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
})

export default ProtectedRoute;