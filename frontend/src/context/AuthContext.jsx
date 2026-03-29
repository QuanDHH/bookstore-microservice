import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [customer, setCustomer] = useState(() => {
    const s = localStorage.getItem('customer')
    return s ? JSON.parse(s) : null
  })
  const [staff, setStaff] = useState(() => {
    const s = localStorage.getItem('staff')
    return s ? JSON.parse(s) : null
  })

  const loginCustomer = (data) => {
    localStorage.setItem('access_token',  data.tokens.access)
    localStorage.setItem('refresh_token', data.tokens.refresh)
    localStorage.setItem('customer', JSON.stringify(data.customer))
    setCustomer(data.customer)
  }

  const loginStaff = (data) => {
    localStorage.setItem('access_token',  data.tokens.access)
    localStorage.setItem('refresh_token', data.tokens.refresh)
    localStorage.setItem('staff', JSON.stringify(data.staff))
    setStaff(data.staff)
  }

  const logout = () => {
    localStorage.clear()
    setCustomer(null)
    setStaff(null)
  }

  return (
    <AuthContext.Provider value={{ customer, staff, loginCustomer, loginStaff, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)