import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { customer, staff, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="navbar-brand">kiemtra01</Link>
        <div className="navbar-links">
          <Link to="/products">Products</Link>
          {customer && <Link to="/cart">Cart</Link>}
          {customer && (
            <button onClick={handleLogout}>Logout</button>
          )}
          {staff && (
            <>
              <Link to="/staff/dashboard">Dashboard</Link>
              <button onClick={handleLogout}>Logout</button>
            </>
          )}
          {!customer && !staff && (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register" className="btn-primary">Register</Link>
              <Link to="/staff/login" style={{ marginLeft: 4, fontSize: '.8rem', opacity: .6 }}>Staff</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}