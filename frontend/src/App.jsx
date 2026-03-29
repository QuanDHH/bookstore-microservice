import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Products from './pages/Products'
import CustomerLogin from './pages/CustomerLogin'
import CustomerRegister from './pages/CustomerRegister'
import Cart from './pages/Cart'
import StaffLogin from './pages/StaffLogin'
import StaffRegister from './pages/StaffRegister'
import StaffDashboard from './pages/StaffDashboard'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/"                  element={<Navigate to="/products" replace />} />
          <Route path="/products"          element={<Products />} />
          <Route path="/login"             element={<CustomerLogin />} />
          <Route path="/register"          element={<CustomerRegister />} />
          <Route path="/cart"              element={<Cart />} />
          <Route path="/staff/login"       element={<StaffLogin />} />
          <Route path="/staff/register"    element={<StaffRegister />} />
          <Route path="/staff/dashboard"   element={<StaffDashboard />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}