import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { staffLogin } from '../api'
import { useAuth } from '../context/AuthContext'

export default function StaffLogin() {
  const [form, setForm]       = useState({ username: '', password: '' })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const { loginStaff }        = useAuth()
  const navigate              = useNavigate()

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async e => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const { data } = await staffLogin(form)
      loginStaff(data)
      navigate('/staff/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1>Staff portal</h1>
        <p className="subtitle">Sign in to manage products</p>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input value={form.username} onChange={set('username')} required autoFocus />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={form.password} onChange={set('password')} required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? <span className="spinner" /> : 'Sign in'}
          </button>
        </form>
        <p className="auth-switch">
          No account? <Link to="/staff/register">Register</Link>
        </p>
      </div>
    </div>
  )
}