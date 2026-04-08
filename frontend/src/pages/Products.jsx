import { useState, useEffect, useCallback } from 'react'
import { getLaptops, getClothes, addToCart } from '../api'
import { useAuth } from '../context/AuthContext'

const PLACEHOLDER = '📦'

function ProductCard({ product, onAddToCart, type }) {
  const [adding, setAdding] = useState(false)

  const handleAdd = async () => {
    setAdding(true)
    await onAddToCart(product, type)
    setAdding(false)
  }

  return (
    <div className="product-card">
      <div className="product-card-img">
        {product.image
          ? <img src={product.image} alt={product.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          : <span>{PLACEHOLDER}</span>}
      </div>
      <div className="product-card-body">
        <div className="product-card-brand">{product.brand}</div>
        <div className="product-card-name">{product.name}</div>
        {type === 'laptop' && (
          <div style={{ fontSize: '.8rem', color: 'var(--muted)', marginBottom: 10 }}>
            {product.cpu} · {product.ram}GB RAM
          </div>
        )}
        {type === 'clothes' && (
          <div style={{ fontSize: '.8rem', color: 'var(--muted)', marginBottom: 10 }}>
            {product.category} · Size {product.size}
          </div>
        )}
        {type === 'mobile' && (
          <div style={{ fontSize: '.8rem', color: 'var(--muted)', marginBottom: 10 }}>
            {product.ram}GB RAM · {product.storage}GB · {product.battery}mAh
          </div>
        )}
        <div className="product-card-footer">
          <span className="product-price">${product.price}</span>
          <span className={`badge ${product.stock > 0 ? 'badge-green' : 'badge-red'}`}>
            {product.stock > 0 ? `${product.stock} left` : 'Out of stock'}
          </span>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', marginTop: 10 }}
          onClick={handleAdd}
          disabled={adding || product.stock === 0}
        >
          {adding ? <span className="spinner" style={{ width: 14, height: 14 }} /> : 'Add to cart'}
        </button>
      </div>
    </div>
  )
}

export default function Products() {
  const [tab, setTab]         = useState('laptops')
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch]   = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [category, setCategory] = useState('')
  const [toast, setToast]     = useState('')
  const { customer }          = useAuth()

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (search)   params.search    = search
      if (minPrice) params.min_price = minPrice
      if (maxPrice) params.max_price = maxPrice
      if (category && tab === 'clothes') params.category = category

      let response
      if (tab === 'laptops')      response = await getLaptops(params)
      else if (tab === 'mobiles') response = await getMobiles(params)
      else                        response = await getClothes(params)

      setProducts(response.data.results || [])
    } catch {
      setProducts([])
    } finally {
      setLoading(false)
    }
  }, [tab, search, minPrice, maxPrice, category])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const handleAddToCart = async (product, type) => {
    if (!customer) { setToast('Please log in to add items to cart'); setTimeout(() => setToast(''), 3000); return }
    try {
      await addToCart(customer.id, {
        product_id:   product.id,
        product_name: product.name,
        quantity:     1,
        price:        product.price,
      })
      setToast(`${product.name} added to cart`)
      setTimeout(() => setToast(''), 2500)
    } catch {
      setToast('Could not add to cart')
      setTimeout(() => setToast(''), 2500)
    }
  }

  return (
    <div className="page">
      <div className="container">
        <div className="products-header">
          <div>
            <h1 className="section-title">Products</h1>
            <p className="text-muted" style={{ marginTop: 4 }}>{products.length} items</p>
          </div>
          <div className="filters">
            <div className="tab-group">
              <button className={tab === 'laptops' ? 'active' : ''} onClick={() => { setTab('laptops'); setCategory('') }}>Laptops</button>
              <button className={tab === 'mobiles'  ? 'active' : ''} onClick={() => setTab('mobiles')}>Mobiles</button>
              <button className={tab === 'clothes'  ? 'active' : ''} onClick={() => setTab('clothes')}>Clothes</button>
            </div>
            <input className="filter-input" placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)} />
            <input className="filter-input" placeholder="Min price" type="number" value={minPrice} onChange={e => setMinPrice(e.target.value)} style={{ width: 110 }} />
            <input className="filter-input" placeholder="Max price" type="number" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} style={{ width: 110 }} />
            {tab === 'clothes' && (
              <select className="filter-input" value={category} onChange={e => setCategory(e.target.value)} style={{ width: 130 }}>
                <option value="">All categories</option>
                {['shirt','pants','dress','jacket','shoes','hat','other'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-center"><div className="spinner" /></div>
        ) : products.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--muted)' }}>No products found.</div>
        ) : (
          <div className="product-grid">
            {products.map(p => (
              <ProductCard key={p.id} product={p} type={tab === 'laptops' ? 'laptop' : tab === 'mobiles' ? 'mobile' : 'clothes'} onAddToCart={handleAddToCart} />
            ))}
          </div>
        )}
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