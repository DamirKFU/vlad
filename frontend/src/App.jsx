import React from "react"
import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import { REFRESH_TOKEN, ACCESS_TOKEN } from "./constants";
import Login from "./pages/Login"
import Home from "./pages/Home"
import Register from "./pages/Register"
import Http404 from "./pages/Http404"
import Constructor from "./pages/Constructor"
import ForgotPassword from "./pages/ForgotPassword"
import Catalog from "./pages/Catalog"
import ProtectedRoute from "./components/ProtectedRoute"
import Cookies from 'js-cookie';
import api from "./api";


function Logout() {
  api.post("users/logout/")
  return <Navigate to="/login"/>
}

function RegisterAndLogout() {
  Cookies.remove(REFRESH_TOKEN);
  Cookies.remove(ACCESS_TOKEN);
  return <Register />
}

function App() {

  return (
      <BrowserRouter>
        <Routes>
          <Route 
            path="/"
            element = {
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
          <Route path="/constructor" element={<Constructor />}/>
          <Route path="/login" element={<Login />}/>
          <Route path="/register" element={<RegisterAndLogout />}/>
          <Route path="/logout" element={<Logout />} /> 
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="*" element={<Http404 />}/>
          <Route path="/catalog" element={<Catalog />}/>
        </Routes>
      </BrowserRouter>
  )
}

export default App

