import { useEffect, useState } from 'react';
import './App.css';

export default function App() {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetch('/api/v1/books')
      .then(response => response.json())
      .then(data => setBooks(data.data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-gray-900 to-slate-950 text-white">
      <Navbar />
      <Hero />
      <Features />
      <ProductCards books={books} />
      <Footer />
    </main>
  );
}

function Navbar() {
  return (
    <header className="sticky top-0 backdrop-blur-lg bg-black/30 z-50">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-6 py-4">
        <div className="text-2xl font-bold">Kitap Satışı</div>
        <nav>
          <ul className="flex space-x-6">
            <li><a href="#features">Özellikler</a></li>
            <li><a href="#products">Ürünler</a></li>
          </ul>
        </nav>
        <button className="bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-lg">
          Ürünleri İncele
        </button>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section
      className="relative w-full h-screen bg-[url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1920&q=80')] bg-cover bg-center"
    >
      <div className="absolute inset-0 bg-black/40" />
      <div className="relative flex flex-col items-center justify-center h-full text-center">
        <h1 className="text-5xl md:text-7xl font-bold">Kitap Okuma Keyfi</h1>
        <p className="mt-4 text-lg">Hayalindeki kitapları bul ve keşfet!</p>
        <button className="mt-6 bg-emerald-500 hover:bg-emerald-400 text-white px-6 py-3 rounded-lg">
          Hemen Başla
        </button>
        <div className="mt-8 flex space-x-4">
          <Counter value={500} label="Kitap" />
          <Counter value={70} label="Yazar" />
        </div>
      </div>
    </section>
  );
}

function Counter({ value, label }) {
  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-lg p-4">
      <h2 className="text-2xl font-bold">{value}</h2>
      <p className="text-white">{label}</p>
    </div>
  );
}

function Features() {
  return (
    <section id="features" className="max-w-6xl mx-auto my-20 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      {featuresData.map((feature, index) => (
        <div key={index} className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 transition-all duration-300 hover:-translate-y-2">
          <div className="text-4xl">{feature.emoji}</div>
          <h3 className="mt-4 text-lg font-semibold">{feature.title}</h3>
          <p className="mt-2 text-gray-300">{feature.description}</p>
        </div>
      ))}
    </section>
  );
}

const featuresData = [
  { emoji: '📚', title: 'Zengin Kütüphane', description: 'Binlerce kitap ve sürekli güncellenen içerik.' },
  { emoji: '👨‍🏫', title: 'Uzman Eğitmenler', description: 'Alanında uzman eğitmenlerle öğrenim.' },
  { emoji: '📖', title: 'Hızlı Erişim', description: 'İstediğin kitaba hızlı ve kolay erişim.' },
];

function ProductCards({ books }) {
  return (
    <section id="products" className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 my-20">
      {books.map((book) => (
        <div key={book.id} className="rounded-2xl overflow-hidden bg-white shadow-lg transition-all duration-300 hover:scale-105">
          <img src="https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80" className="w-full h-48 object-cover" alt={book.title} />
          <div className="p-6">
            <h3 className="text-xl font-bold">{book.title}</h3>
            <p className="mt-2 text-gray-600">{book.author}</p>
            <p className="mt-2 text-lg text-emerald-500">₺20</p>
            <button onClick={() => handleOrder(book)} className="mt-4 bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-lg">
              Sipariş Ver
            </button>
          </div>
        </div>
      ))}
    </section>
  );
}

// Bug fix: Implement the order handling for the order button to work.
function handleOrder(book) {
  console.log(`Sipariş verildi: ${book.title}`);
}

function Footer() {
  return (
    <footer className="bg-black/50 py-8">
      <div className="max-w-6xl mx-auto text-center">
        <div className="mb-4">
          <a href="#" className="text-gray-300 hover:text-white">Link 1</a>
          <span className="mx-2">|</span>
          <a href="#" className="text-gray-300 hover:text-white">Link 2</a>
        </div>
        <p className="text-gray-500">© 2023 Kitap Satışı. Tüm Hakları Saklıdır.</p>
      </div>
    </footer>
  );
}