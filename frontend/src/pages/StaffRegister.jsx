import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { staffRegister } from '../api'
import { useAuth } from '../context/AuthContext'

export default function StaffRegister() {
  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '',
    full_name: '', phone_number: '', address: '', date_of_birth: '', role: 'staff',
  })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const { loginStaff }        = useAuth()
  const navigate              = useNavigate()

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async e => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const { data } = await staffRegister(form)
      loginStaff(data)
      navigate('/staff/dashboard')
    } catch (err) {
      const d = err.response?.data
      if (d && typeof d === 'object') {
        setError(Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`).join('\n'))
      } else {
        setError('Registration failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1>Staff registration</h1>
        <p className="subtitle">Create a staff account</p>
        {error && <div className="alert alert-error" style={{ whiteSpace: 'pre-line' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Username</label>
              <input value={form.username} onChange={set('username')} required autoFocus />
            </div>
            <div className="form-group">
              <label>Full name</label>
              <input value={form.full_name} onChange={set('full_name')} required />
            </div>
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={set('email')} required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={set('password')} required />
            </div>
            <div className="form-group">
              <label>Confirm password</label>
              <input type="password" value={form.password2} onChange={set('password2')} required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Phone</label>
              <input value={form.phone_number} onChange={set('phone_number')} />
            </div>
            <div className="form-group">
              <label>Role</label>
              <select value={form.role} onChange={set('role')}>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Date of birth</label>
            <input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? <span className="spinner" /> : 'Create account'}
          </button>
        </form>
        <p className="auth-switch">Already registered? <Link to="/staff/login">Sign in</Link></p>
      </div>
    </div>
  )
}