const canvas = document.getElementById("tetris");
const context = canvas.getContext("2d");
canvas.width = 240;
canvas.height = 400;

const row = 20;
const column = 10;
const scoreElement = document.getElementById("score");
let score = 0;

const colors = [
    null,
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "purple",
    "cyan"
];

const shapes = [
    [],
    [[1, 1, 1, 1]], // I
    [[1, 1, 1], [0, 1, 0]], // T
    [[1, 1], [1, 1]], // O
    [[0, 1, 1], [1, 1, 0]], // S
    [[1, 1, 0], [0, 1, 1]], // Z
    [[1, 1, 1], [1, 0, 0]], // L
    [[1, 1, 1], [0, 0, 1]], // J
];

let board = Array.from({ length: row }, () => Array(column).fill(0));

class Piece {
    constructor(type) {
        this.type = type;
        this.shape = shapes[type];
        this.color = colors[type];
        this.x = Math.floor(column / 2) - 1;
        this.y = 0;
    }

    draw() {
        context.fillStyle = this.color;
        this.shape.forEach((row, rIndex) => {
            row.forEach((value, cIndex) => {
                if (value) {
                    context.fillRect(this.x + cIndex, this.y + rIndex, 1, 1);
                }
            });
        });
    }

    move(dir) {
        this.x += dir;
        if (this.collide()) {
            this.x -= dir;
        }
    }

    drop() {
        this.y++;
        if (this.collide()) {
            this.y--;
            this.merge();
            return true;
        }
        return false;
    }

    collide() {
        return this.shape.some((row, rIndex) =>
            row.some((value, cIndex) =>
                value && (this.y + rIndex >= row || this.x + cIndex < 0 || this.x + cIndex >= column || board[this.y + rIndex][this.x + cIndex])
            )
        );
    }

    merge() {
        this.shape.forEach((row, rIndex) => {
            row.forEach((value, cIndex) => {
                if (value) board[this.y + rIndex][this.x + cIndex] = this.type;
            });
        });
        this.clearRows();
        this.reset();
    }

    clearRows() {
        for (let r = row - 1; r >= 0; r--) {
            if (board[r].every(value => value !== 0)) {
                score += 10;
                board.splice(r, 1);
                board.unshift(Array(column).fill(0));
                r++;
            }
        }
        scoreElement.innerText = `Score: ${score}`;
    }

    reset() {
        const nextPiece = Math.floor(Math.random() * (shapes.length - 1)) + 1;
        this.type = nextPiece;
        this.shape = shapes[nextPiece];
        this.color = colors[nextPiece];
        this.x = Math.floor(column / 2) - 1;
        this.y = 0;

        if (this.collide()) {
            alert("Game Over!");
            board = Array.from({ length: row }, () => Array(column).fill(0));
            score = 0;
            scoreElement.innerText = `Score: ${score}`;
        }
    }
}

const drawBoard = () => {
    context.clearRect(0, 0, canvas.width, canvas.height);
    board.forEach((row, rIndex) => {
        row.forEach((value, cIndex) => {
            if (value) {
                context.fillStyle = colors[value];
                context.fillRect(cIndex, rIndex, 1, 1);
            }
        });
    });
};

let currentPiece = new Piece(Math.floor(Math.random() * (shapes.length - 1)) + 1);

const update = () => {
    if (currentPiece.drop()) {
        currentPiece = new Piece(Math.floor(Math.random() * (shapes.length - 1)) + 1);
    }
    drawBoard();
    currentPiece.draw();
};

document.addEventListener("keydown", (e) => {
    switch (e.key) {
        case "ArrowLeft":
            currentPiece.move(-1);
            break;
        case "ArrowRight":
            currentPiece.move(1);
            break;
        case "ArrowDown":
            currentPiece.drop();
            break;
        case "ArrowUp":
            // Rotate piece (not implemented)
            break;
    }
    drawBoard();
    currentPiece.draw();
});

setInterval(update, 1000);