import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getLaptops, getClothes, createLaptop, updateLaptop, createClothes, updateClothes } from '../api'
import { useAuth } from '../context/AuthContext'

const LAPTOP_DEFAULTS  = { name: '', brand: '', cpu: '', ram: '', price: '', stock: '' }
const CLOTHES_DEFAULTS = { name: '', brand: '', category: 'shirt', size: 'M', price: '', stock: '' }
const MOBILE_DEFAULTS = { name: '', brand: '', ram: '', storage: '', battery: '', price: '', stock: '' }

function LaptopForm({ initial, onSubmit, loading }) {
  const [form, setForm] = useState(initial || LAPTOP_DEFAULTS)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))
  const handleSubmit = e => { e.preventDefault(); onSubmit(form) }

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-row">
        <div className="form-group"><label>Name</label><input value={form.name} onChange={set('name')} required /></div>
        <div className="form-group"><label>Brand</label><input value={form.brand} onChange={set('brand')} required /></div>
      </div>
      <div className="form-row">
        <div className="form-group"><label>CPU</label><input value={form.cpu} onChange={set('cpu')} required /></div>
        <div className="form-group"><label>RAM (GB)</label><input type="number" value={form.ram} onChange={set('ram')} required /></div>
      </div>
      <div className="form-row">
        <div className="form-group"><label>Price ($)</label><input type="number" step="0.01" value={form.price} onChange={set('price')} required /></div>
        <div className="form-group"><label>Stock</label><input type="number" value={form.stock} onChange={set('stock')} required /></div>
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? <span className="spinner" /> : (initial ? 'Update laptop' : 'Add laptop')}
      </button>
    </form>
  )
}

function ClothesForm({ initial, onSubmit, loading }) {
  const [form, setForm] = useState(initial || CLOTHES_DEFAULTS)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))
  const handleSubmit = e => { e.preventDefault(); onSubmit(form) }

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-row">
        <div className="form-group"><label>Name</label><input value={form.name} onChange={set('name')} required /></div>
        <div className="form-group"><label>Brand</label><input value={form.brand} onChange={set('brand')} required /></div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Category</label>
          <select value={form.category} onChange={set('category')}>
            {['shirt','pants','dress','jacket','shoes','hat','other'].map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Size</label>
          <select value={form.size} onChange={set('size')}>
            {['XS','S','M','L','XL','XXL'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-group"><label>Price ($)</label><input type="number" step="0.01" value={form.price} onChange={set('price')} required /></div>
        <div className="form-group"><label>Stock</label><input type="number" value={form.stock} onChange={set('stock')} required /></div>
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? <span className="spinner" /> : (initial ? 'Update clothes' : 'Add clothes')}
      </button>
    </form>
  )
}

function MobileForm({ initial, onSubmit, loading }) {
  const [form, setForm] = useState(initial || MOBILE_DEFAULTS)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))
  const handleSubmit = e => { e.preventDefault(); onSubmit(form) }

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-row">
        <div className="form-group"><label>Name</label><input value={form.name} onChange={set('name')} required /></div>
        <div className="form-group"><label>Brand</label><input value={form.brand} onChange={set('brand')} required /></div>
      </div>
      <div className="form-row">
        <div className="form-group"><label>RAM (GB)</label><input type="number" value={form.ram} onChange={set('ram')} required /></div>
        <div className="form-group"><label>Storage (GB)</label><input type="number" value={form.storage} onChange={set('storage')} required /></div>
      </div>
      <div className="form-row">
        <div className="form-group"><label>Battery (mAh)</label><input type="number" value={form.battery} onChange={set('battery')} required /></div>
        <div className="form-group"><label>Price ($)</label><input type="number" step="0.01" value={form.price} onChange={set('price')} required /></div>
      </div>
      <div className="form-group"><label>Stock</label><input type="number" value={form.stock} onChange={set('stock')} required /></div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? <span className="spinner" /> : (initial ? 'Update mobile' : 'Add mobile')}
      </button>
    </form>
  )
}

export default function StaffDashboard() {
  const { staff }         = useAuth()
  const navigate          = useNavigate()
  const [view, setView]   = useState('laptops-list')
  const [laptops, setLaptops]   = useState([])
  const [clothes, setClothes]   = useState([])
  const [mobiles, setMobiles]   = useState([])
  const [editing, setEditing]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [toast, setToast]       = useState('')

  useEffect(() => { if (!staff) navigate('/staff/login') }, [staff])

  useEffect(() => {
    if (view === 'laptops-list')  getLaptops().then(r => setLaptops(r.data.results || []))
    if (view === 'clothes-list')  getClothes().then(r => setClothes(r.data.results || []))
    if (view === 'mobiles-list') getMobiles().then(r => setMobiles(r.data.results || []))
  }, [view])

  const showToast = msg => { setToast(msg); setTimeout(() => setToast(''), 2500) }

  const handleLaptopSubmit = async (form) => {
    setLoading(true)
    try {
      if (editing) { await updateLaptop(editing.id, form); showToast('Laptop updated') }
      else         { await createLaptop(form);             showToast('Laptop added') }
      setView('laptops-list'); setEditing(null)
    } catch (err) {
      showToast(err.response?.data?.detail || 'Error saving laptop')
    } finally { setLoading(false) }
  }

  const handleClothesSubmit = async (form) => {
    setLoading(true)
    try {
      if (editing) { await updateClothes(editing.id, form); showToast('Clothes updated') }
      else         { await createClothes(form);             showToast('Clothes added') }
      setView('clothes-list'); setEditing(null)
    } catch (err) {
      showToast(err.response?.data?.detail || 'Error saving clothes')
    } finally { setLoading(false) }
  }

  const handleMobileSubmit = async (form) => {
    setLoading(true)
    try {
      if (editing) { await updateMobile(editing.id, form); showToast('Mobile updated') }
      else         { await createMobile(form);              showToast('Mobile added') }
      setView('mobiles-list'); setEditing(null)
    } catch (err) {
      showToast(err.response?.data?.detail || 'Error saving mobile')
    } finally { setLoading(false) }
  }

  const startEdit = (item, type) => {
    setEditing(item)
    if (type === 'laptop')      setView('laptops-form')
    else if (type === 'mobile') setView('mobiles-form')
    else                        setView('clothes-form')
  }

  return (
    <div className="page">
      <div className="container">
        <div className="staff-layout">
          <aside className="staff-sidebar">
            <h2>Laptops</h2>
            <button className={`sidebar-item ${view === 'laptops-list' ? 'active' : ''}`} onClick={() => { setView('laptops-list'); setEditing(null) }}>All laptops</button>
            <button className={`sidebar-item ${view === 'laptops-form' && !editing ? 'active' : ''}`} onClick={() => { setView('laptops-form'); setEditing(null) }}>Add laptop</button>
            <h2 style={{ marginTop: 20 }}>Clothes</h2>
            <button className={`sidebar-item ${view === 'clothes-list' ? 'active' : ''}`} onClick={() => { setView('clothes-list'); setEditing(null) }}>All clothes</button>
            <button className={`sidebar-item ${view === 'clothes-form' && !editing ? 'active' : ''}`} onClick={() => { setView('clothes-form'); setEditing(null) }}>Add clothes</button>
            <h2 style={{ marginTop: 20 }}>Mobiles</h2>
            <button className={`sidebar-item ${view === 'mobiles-list' ? 'active' : ''}`}
              onClick={() => { setView('mobiles-list'); setEditing(null) }}>All mobiles</button>
            <button className={`sidebar-item ${view === 'mobiles-form' && !editing ? 'active' : ''}`}
              onClick={() => { setView('mobiles-form'); setEditing(null) }}>Add mobile</button>
          </aside>

          <main className="staff-content">
            {view === 'laptops-list' && (
              <>
                <h2>Laptops</h2>
                <table className="product-table">
                  <thead><tr><th>Name</th><th>Brand</th><th>CPU</th><th>RAM</th><th>Price</th><th>Stock</th><th></th></tr></thead>
                  <tbody>
                    {laptops.map(l => (
                      <tr key={l.id}>
                        <td>{l.name}</td><td>{l.brand}</td><td>{l.cpu}</td>
                        <td>{l.ram}GB</td><td>${l.price}</td><td>{l.stock}</td>
                        <td><button className="btn btn-secondary btn-sm" onClick={() => startEdit(l, 'laptop')}>Edit</button></td>
                      </tr>
                    ))}
                    {laptops.length === 0 && <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px 0' }}>No laptops yet.</td></tr>}
                  </tbody>
                </table>
              </>
            )}

            {view === 'laptops-form' && (
              <>
                <h2>{editing ? 'Edit laptop' : 'Add laptop'}</h2>
                <LaptopForm initial={editing} onSubmit={handleLaptopSubmit} loading={loading} />
              </>
            )}

            {view === 'clothes-list' && (
              <>
                <h2>Clothes</h2>
                <table className="product-table">
                  <thead><tr><th>Name</th><th>Brand</th><th>Category</th><th>Size</th><th>Price</th><th>Stock</th><th></th></tr></thead>
                  <tbody>
                    {clothes.map(c => (
                      <tr key={c.id}>
                        <td>{c.name}</td><td>{c.brand}</td><td>{c.category}</td>
                        <td>{c.size}</td><td>${c.price}</td><td>{c.stock}</td>
                        <td><button className="btn btn-secondary btn-sm" onClick={() => startEdit(c, 'clothes')}>Edit</button></td>
                      </tr>
                    ))}
                    {clothes.length === 0 && <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px 0' }}>No clothes yet.</td></tr>}
                  </tbody>
                </table>
              </>
            )}

            {view === 'clothes-form' && (
              <>
                <h2>{editing ? 'Edit clothes' : 'Add clothes'}</h2>
                <ClothesForm initial={editing} onSubmit={handleClothesSubmit} loading={loading} />
              </>
            )}

            {view === 'mobiles-list' && (
              <>
                <h2>Mobiles</h2>
                <table className="product-table">
                  <thead><tr><th>Name</th><th>Brand</th><th>RAM</th><th>Storage</th><th>Battery</th><th>Price</th><th>Stock</th><th></th></tr></thead>
                  <tbody>
                    {mobiles.map(m => (
                      <tr key={m.id}>
                        <td>{m.name}</td><td>{m.brand}</td><td>{m.ram}GB</td>
                        <td>{m.storage}GB</td><td>{m.battery}mAh</td><td>${m.price}</td><td>{m.stock}</td>
                        <td><button className="btn btn-secondary btn-sm" onClick={() => startEdit(m, 'mobile')}>Edit</button></td>
                      </tr>
                    ))}
                    {mobiles.length === 0 && <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px 0' }}>No mobiles yet.</td></tr>}
                  </tbody>
                </table>
              </>
            )}

            {view === 'mobiles-form' && (
              <>
                <h2>{editing ? 'Edit mobile' : 'Add mobile'}</h2>
                <MobileForm initial={editing} onSubmit={handleMobileSubmit} loading={loading} />
              </>
            )}
          </main>
        </div>
      </div>

      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
          background: 'var(--accent)', color: 'var(--accent-fg)',
          padding: '10px 20px', borderRadius: 'var(--radius)', fontSize: '.875rem',
          boxShadow: '0 4px 16px rgba(0,0,0,.15)', zIndex: 200,
        }}>{toast}</div>
      )}
    </div>
  )
}