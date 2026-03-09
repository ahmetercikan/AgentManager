// tetris_game.js

// Oyun alanı boyutları
const ROWS = 20;
const COLS = 10;

// Oyun alanı
let board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));

// Blok çeşitleri
const BLOCKS = {
    T: [[1, 1, 1], [0, 1, 0]],
    L: [[1, 0, 0], [1, 1, 1]],
    I: [[1, 1, 1, 1]],
    O: [[1, 1], [1, 1]],
    S: [[0, 1, 1], [1, 1, 0]],
    Z: [[1, 1, 0], [0, 1, 1]]
};

// Aktif blok
let currentBlock;
let position = { x: 0, y: 0 };
let score = 0;
let gameOver = false;

// Rastgele blok seçimi
function getRandomBlock() {
    const blocks = Object.keys(BLOCKS);
    const randomIndex = Math.floor(Math.random() * blocks.length);
    return { shape: BLOCKS[blocks[randomIndex]], type: blocks[randomIndex] };
}

// Oyun alanını görüntüle
function drawBoard() {
    // Temizle
    const gameArea = document.getElementById('gameArea');
    gameArea.innerHTML = '';
    
    board.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'row';
        row.forEach(cell => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'cell';
            if (cell) cellDiv.classList.add('filled');
            rowDiv.appendChild(cellDiv);
        });
        gameArea.appendChild(rowDiv);
    });
    
    const scoreDiv = document.getElementById('score');
    scoreDiv.innerText = `Score: ${score}`;
}

// Bloğun yerleştirilmesi
function placeBlock() {
    currentBlock.shape.forEach((row, r) => {
        row.forEach((cell, c) => {
            if (cell) {
                board[position.y + r][position.x + c] = 1;
            }
        });
    });
}

// Satırları kontrol et
function checkRows() {
    for (let r = 0; r < ROWS; r++) {
        if (board[r].every(cell => cell === 1)) {
            board.splice(r, 1);
            board.unshift(Array(COLS).fill(0));
            score += 100; // Her tam satır için 100 puan
        }
    }
}

// Oyun bitiş koşulunu kontrol et
function checkGameOver() {
    if (board[0].some(cell => cell === 1)) {
        gameOver = true;
        alert("Game Over!");
    }
}

// Bloğu hareket ettirin
function moveBlock(dir) {
    position.x += dir;
    if (position.x < 0 || position.x + currentBlock.shape[0][0].length > COLS || collision()) {
        position.x -= dir;
    }
    drawBoard();
}

// Bloğu döndür
function rotateBlock() {
    const oldShape = currentBlock.shape;
    currentBlock.shape = currentBlock.shape[0].map((val, index) =>
        currentBlock.shape.map(row => row[index]).reverse());
    if (collision()) {
        currentBlock.shape = oldShape; // Döndürme çarpışma yapıyorsa eski haline getir
    }
    drawBoard();
}

// Çarpışma kontrolü
function collision() {
    return currentBlock.shape.some((row, r) => {
        return row.some((cell, c) => {
            if (cell) {
                const newY = position.y + r;
                const newX = position.x + c;
                return newY >= ROWS || newX < 0 || newX >= COLS || board[newY] && board[newY][newX] === 1;
            }
            return false;
        });
    });
}

// Güncellemeleri kontrol et
function update() {
    if (!gameOver) {
        position.y++;
        if (collision()) {
            position.y--;
            placeBlock();
            checkRows();
            checkGameOver();
            currentBlock = getRandomBlock();
            position.x = Math.floor(COLS / 2) - Math.floor(currentBlock.shape[0].length / 2);
        }
        drawBoard();
    }
}

// Oyun döngüsü
function gameLoop() {
    update();
    setTimeout(gameLoop, 1000);
}

// Klavye girişlerini dinle
document.addEventListener('keydown', (event) => {
    if (event.key === "ArrowLeft") moveBlock(-1);
    if (event.key === "ArrowRight") moveBlock(1);
    if (event.key === "ArrowDown") moveBlock(0); // Aşağı doğru hızlandırma
    if (event.key === "ArrowUp") rotateBlock();
});

// Oyun başlangıcı
function startGame() {
    board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    score = 0;
    gameOver = false;
    currentBlock = getRandomBlock();
    position = { x: Math.floor(COLS / 2) - Math.floor(currentBlock.shape[0].length / 2), y: 0 };
    gameLoop();
}

// HTML dosyasında oyunun başlatılması için bir fonksiyon ekleyin
// document.getElementById("startButton").addEventListener("click", startGame);