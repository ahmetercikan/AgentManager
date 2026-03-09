import React, { useState, useEffect } from "react";
import "./App.css";

const MOCK_PRODUCTS = [
  { id: 1, name: "Kablosuz Kulaklık", description: "Bluetooth 5.0, aktif gürültü engelleme", price: 1299 },
  { id: 2, name: "Akıllı Saat", description: "Kalp ritmi, adım sayar, su geçirmez", price: 2499 },
  { id: 3, name: "Mekanik Klavye", description: "RGB aydınlatma, Cherry MX Blue switch", price: 899 },
  { id: 4, name: "Webcam HD", description: "1080p, otomatik odaklama, geniş açı", price: 649 },
  { id: 5, name: "USB-C Hub", description: "7-in-1, HDMI, USB 3.0, SD kart", price: 399 },
  { id: 6, name: "Monitör Standı", description: "Ayarlanabilir yükseklik, alüminyum", price: 549 },
];

const App = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setTimeout(() => {
      setProducts(MOCK_PRODUCTS);
      setLoading(false);
    }, 500);
  }, []);

  const handleAddToCart = (productId) => {
    const product = products.find(p => p.id === productId);
    alert(`${product.name} sepetinize eklendi!`);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>E-Ticaret Ürünleri</h1>
        <span className="cart-icon" role="img" aria-label="Sepet">🛒</span>
      </header>
      <main className="product-list">
        {loading && <p>Yükleniyor...</p>}
        {error && <p className="error">{error}</p>}
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <img src={`https://via.placeholder.com/150?text=${encodeURIComponent(product.name)}`} alt={product.name} />
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <p className="price">{product.price} ₺</p>
            <button
              onClick={() => handleAddToCart(product.id)}
              className="add-to-cart"
              aria-label={`Sepete ekle ${product.name}`}
            >
              Sepete Ekle
            </button>
          </div>
        ))}
      </main>
    </div>
  );
};

export default App;
