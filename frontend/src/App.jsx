import React from "react"
import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import Login from "./pages/Login"
import Home from "./pages/Home"
import Register from "./pages/Register"
import Http404 from "./pages/Http404"
import ProtectedRoute from "./components/ProtectedRoute"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login"/>
}

function RegisterAndLogout() {
  localStorage.clear()
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
          <Route path="/login" element={<Login />}/>
          <Route path="/register" element={<RegisterAndLogout />}/>
          <Route path="/logout" element={<Logout />} />
          <Route path="*" element={<Http404 />}/>
        </Routes>
      </BrowserRouter>
  )
}

export default App
