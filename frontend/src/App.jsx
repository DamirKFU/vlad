import React from "react"
import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import { REFRESH_TOKEN, ACCESS_TOKEN } from "./constants";
import Login from "./pages/Login"
import Home from "./pages/Home"
import Register from "./pages/Register"
import Http404 from "./pages/Http404"
import Constructor from "./pages/Constructor"
import ForgotPassword from "./pages/ForgotPassword"
import ProductDetail from "./pages/ProductDetail"
import Catalog from "./pages/Catalog"
import ProtectedRoute from "./components/ProtectedRoute"
import Cookies from 'js-cookie';
import api from "./api";
import Cart from './pages/Cart';
import OrderHistory from './pages/OrderHistory';
import Checkout from './pages/Checkout';
import OrderDetail from './pages/OrderDetail';
import StaffOrders from './pages/StaffOrders';
import StaffOrderDetail from './pages/StaffOrderDetail';
import TelegramAuth from './pages/TelegramAuth';


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
          <Route path="/product/:productId" element={<ProductDetail />}/>
          <Route path="/cart" element={<Cart />} />
          <Route path="/orders" element={<OrderHistory />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/orders/:orderId" element={<OrderDetail />} />
          <Route path="/staff/orders" element={<StaffOrders />} />
          <Route path="/staff/orders/:orderId" element={<StaffOrderDetail />} />
          <Route path="/telegram-auth" element={<TelegramAuth />} />
        </Routes>
      </BrowserRouter>
  )
}

export default App

