import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { RiShoppingCartLine } from "react-icons/ri";

const App = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get("/api/products");
        setProducts(response.data);
      } catch (err) {
        setError("Ürünleri yüklerken bir hata oluştu.");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const handleAddToCart = async (productId) => {
    try {
      await axios.post("/api/cart", {
        user_id: 1, // for example
        product_id: productId,
        quantity: 1,
      });
      alert("Ürün sepetinize eklendi!");
    } catch (err) {
      setError("Sepete eklerken bir hata oluştu.");
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>E-Ticaret Ürünleri</h1>
        <RiShoppingCartLine className="cart-icon" aria-label="Sepet" />
      </header>
      <main className="product-list">
        {loading && <p>Yükleniyor...</p>}
        {error && <p className="error">{error}</p>}
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <img src={`https://via.placeholder.com/150`} alt={product.name} />
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <p>{product.price} ₺</p>
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