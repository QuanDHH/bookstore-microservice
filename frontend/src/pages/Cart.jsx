import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCart, removeFromCart } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Cart() {
  const { customer }      = useAuth()
  const [cart, setCart]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [removing, setRemoving] = useState(null)

  useEffect(() => {
    if (!customer) return
    getCart(customer.id)
      .then(r => setCart(r.data))
      .catch(() => setCart(null))
      .finally(() => setLoading(false))
  }, [customer])

  const handleRemove = async (productId) => {
    setRemoving(productId)
    try {
      const { data } = await removeFromCart(customer.id, { product_id: productId })
      setCart(data)
    } catch {}
    setRemoving(null)
  }

  if (!customer) return (
    <div className="page">
      <div className="container">
        <div className="cart-empty">
          <p>Please <Link to="/login" style={{ borderBottom: '1px solid var(--border)' }}>log in</Link> to view your cart.</p>
        </div>
      </div>
    </div>
  )

  if (loading) return <div className="page"><div className="loading-center"><div className="spinner" /></div></div>

  const items = cart?.items || []

  return (
    <div className="page">
      <div className="container">
        <div style={{ padding: '32px 0 20px' }}>
          <h1 className="section-title">Your cart</h1>
        </div>

        {items.length === 0 ? (
          <div className="cart-empty">
            <p>Your cart is empty.</p>
            <Link to="/products" className="btn btn-primary">Browse products</Link>
          </div>
        ) : (
          <div className="cart-layout">
            <div className="cart-items">
              {items.map(item => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-info">
                    <div className="cart-item-name">{item.product_name}</div>
                    <div className="cart-item-meta">Qty: {item.quantity} · ${item.price} each</div>
                  </div>
                  <span className="cart-item-price">${item.subtotal}</span>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleRemove(item.product_id)}
                    disabled={removing === item.product_id}
                  >
                    {removing === item.product_id ? <span className="spinner" style={{ width: 14, height: 14 }} /> : 'Remove'}
                  </button>
                </div>
              ))}
            </div>

            <div className="cart-summary">
              <h3>Order summary</h3>
              {items.map(item => (
                <div key={item.id} className="summary-row">
                  <span>{item.product_name} ×{item.quantity}</span>
                  <span>${item.subtotal}</span>
                </div>
              ))}
              <div className="summary-row total">
                <span>Total</span>
                <span>${cart.total_price}</span>
              </div>
              <button className="btn btn-primary" style={{ width: '100%', marginTop: 16 }}>
                Checkout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}