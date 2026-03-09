import React, { useState, useEffect } from "react";
import axios from "axios";
import './Game.css'; // Özel stil sayfaları için

const Game = () => {
  const [snakePosition, setSnakePosition] = useState([]);
  const [score, setScore] = useState(0);
  const [userId, setUserId] = useState(null);
  const [direction, setDirection] = useState("right");
  const [gameStarted, setGameStarted] = useState(false);

  // Oyunu başlatma
  const startGame = async (username) => {
    try {
      const response = await axios.post("/api/game/start", { username });
      setUserId(response.data.user_id);
      setSnakePosition([(5, 5)]); // Başlangıç pozisyonu
      setScore(0);
      setGameStarted(true);
    } catch (error) {
      console.error("Error starting game:", error);
      alert("Oyunu başlatırken bir hata oluştu!");
    }
  };

  // Yılanı hareket ettirme
  const moveSnake = async () => {
    try {
      if (userId) {
        const response = await axios.put("/api/game/move", { user_id: userId, direction });
        setSnakePosition(response.data.snake_position);
        setScore(response.data.score);
      }
    } catch (error) {
      console.error("Error moving snake:", error);
      alert("Yılanı hareket ettirirken bir hata oluştu!");
    }
  };

  // Oyunun durumunu güncelle
  const updateStatus = async () => {
    if (userId) {
      try {
        const response = await axios.get(`/api/game/status?user_id=${userId}`);
        setSnakePosition(response.data.snake_position);
        setScore(response.data.score);
      } catch (error) {
        console.error("Error fetching game status:", error);
        alert("Oyun durumu alınırken bir hata oluştu!");
      }
    }
  };

  // Klavye ile yönlendirme
  const handleKeyPress = (event) => {
    switch (event.key) {
      case "ArrowUp":
        setDirection("up");
        break;
      case "ArrowDown":
        setDirection("down");
        break;
      case "ArrowLeft":
        setDirection("left");
        break;
      case "ArrowRight":
        setDirection("right");
        break;
      default:
        break;
    }
  };

  // Oyunun başlangıcı
  useEffect(() => {
    window.addEventListener("keydown", handleKeyPress);
    if (gameStarted) {
      const intervalId = setInterval(() => {
        moveSnake();
        updateStatus();
      }, 300); // Yılanın hareket etme süresi

      return () => clearInterval(intervalId);
    }
  }, [gameStarted, direction]);

  return (
    <div className="game-container">
      <h1>Yılan Oyunu</h1>
      {!gameStarted ? (
        <button onClick={() => startGame(prompt("Kullanıcı adını girin:"))}>Oyunu Başlat</button>
      ) : (
        <>
          <div className="score-board">
            <h2>Skor: {score}</h2>
          </div>
          <div className="game-board">
            {snakePosition.map((segment, index) => (
              <div
                key={index}
                className="snake-segment"
                style={{
                  left: `${segment[0] * 20}px`,
                  top: `${segment[1] * 20}px`,
                }}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Game;