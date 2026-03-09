import { useEffect, useState } from 'react';
import './App.css';

function App() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await fetch('/api/v1/orders');
                if (!response.ok) throw new Error('Bir hata oluştu');
                const data = await response.json();
                setOrders(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, []);

    const handleOrder = async (itemName) => {
        try {
            const response = await fetch('/api/v1/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ item_name: itemName, user_id: 1 }),
            });
            if (!response.ok) throw new Error('Sipariş oluşturulamadı');
            const newOrder = await response.json();
            setOrders((prevOrders) => [...prevOrders, newOrder]);
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-indigo-950 to-slate-900 flex flex-col items-center">
            <h1 className="text-white text-3xl font-semibold mt-10">Hamburger Sipariş Arayüzü</h1>

            {loading && <p className="text-white mt-5">Yükleniyor...</p>}
            {error && <p className="text-red-500 mt-5">{error}</p>}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-10 px-4">
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white">Klasik Hamburger</h2>
                    <button 
                        onClick={() => handleOrder("Klasik Hamburger")} 
                        className="mt-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 transition-transform duration-300 ease-in-out transform hover:-translate-y-1"
                    >
                        Sipariş Ver
                    </button>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white">Double Cheese Burger</h2>
                    <button 
                        onClick={() => handleOrder("Double Cheese Burger")} 
                        className="mt-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 transition-transform duration-300 ease-in-out transform hover:-translate-y-1"
                    >
                        Sipariş Ver
                    </button>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white">Vegan Hamburger</h2>
                    <button 
                        onClick={() => handleOrder("Vegan Hamburger")} 
                        className="mt-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 transition-transform duration-300 ease-in-out transform hover:-translate-y-1"
                    >
                        Sipariş Ver
                    </button>
                </div>
            </div>
            
            {orders.length > 0 && (
                <div className="mt-10">
                    <h2 className="text-white text-2xl font-semibold">Siparişlerim</h2>
                    <ul className="mt-4">
                        {orders.map((order) => (
                            <li key={order.id} className="text-white">{order.item_name}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default App;