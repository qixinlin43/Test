let gameState = null;
let selectedSquare = null;
let humanColor = null;
let moveHistory = [];

const whiteBtn = document.getElementById('whiteBtn');
const blackBtn = document.getElementById('blackBtn');
const newGameBtn = document.getElementById('newGameBtn');
const statusDiv = document.getElementById('status');
const chessboard = document.getElementById('chessboard');
const moveHistoryDiv = document.getElementById('moveHistory');

whiteBtn.addEventListener('click', () => startNewGame('white'));
blackBtn.addEventListener('click', () => startNewGame('black'));
newGameBtn.addEventListener('click', () => location.reload());

function startNewGame(color) {
    humanColor = color;
    moveHistory = [];

    fetch('/api/new_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: 'default', human_color: color })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data;
            whiteBtn.style.display = 'none';
            blackBtn.style.display = 'none';
            newGameBtn.style.display = 'inline-block';
            renderBoard(data.board);
            updateStatus(data);

            if (data.computer_move) {
                addMoveToHistory('Computer', data.computer_move.from, data.computer_move.to);
            }
        }
    });
}

function renderBoard(board) {
    chessboard.innerHTML = '';

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = 'square';
            square.className += (row + col) % 2 === 0 ? ' light' : ' dark';
            square.dataset.row = row;
            square.dataset.col = col;
            square.dataset.position = positionToString(row, col);

            const piece = board[row][col];
            if (piece) {
                const pieceSpan = document.createElement('span');
                pieceSpan.className = 'piece';
                pieceSpan.textContent = piece.symbol;
                square.appendChild(pieceSpan);
            }

            square.addEventListener('click', handleSquareClick);
            chessboard.appendChild(square);
        }
    }
}

function handleSquareClick(event) {
    const square = event.currentTarget;
    const position = square.dataset.position;

    if (!gameState || gameState.game_over) return;
    if (gameState.current_player !== humanColor) return;

    // If clicking the same square, deselect
    if (selectedSquare === position) {
        clearSelection();
        return;
    }

    // If a square is already selected, try to move
    if (selectedSquare) {
        makeMove(selectedSquare, position);
    } else {
        // Select this square if it has a piece of the current player's color
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        const piece = gameState.board[row][col];

        if (piece && piece.color === humanColor) {
            selectSquare(position);
        }
    }
}

function selectSquare(position) {
    clearSelection();
    selectedSquare = position;

    const square = document.querySelector(`[data-position="${position}"]`);
    square.classList.add('selected');

    // Highlight legal moves
    fetch('/api/legal_moves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: 'default', from: position })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            data.legal_moves.forEach(movePos => {
                const moveSquare = document.querySelector(`[data-position="${movePos}"]`);
                moveSquare.classList.add('legal-move');
                if (moveSquare.querySelector('.piece')) {
                    moveSquare.classList.add('has-piece');
                }
            });
        }
    });
}

function clearSelection() {
    selectedSquare = null;
    document.querySelectorAll('.square').forEach(sq => {
        sq.classList.remove('selected', 'legal-move', 'has-piece');
    });
}

function makeMove(from, to) {
    fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: 'default', from: from, to: to })
    })
    .then(response => response.json())
    .then(data => {
        clearSelection();

        if (data.success) {
            gameState = data;
            renderBoard(data.board);
            addMoveToHistory('You', from, to);

            if (data.computer_move) {
                setTimeout(() => {
                    addMoveToHistory('Computer', data.computer_move.from, data.computer_move.to);
                    updateStatus(data);
                }, 300);
            } else {
                updateStatus(data);
            }
        } else {
            alert('Invalid move: ' + data.error);
        }
    });
}

function updateStatus(data) {
    if (data.game_over) {
        if (data.winner === 'draw') {
            statusDiv.textContent = 'Game Over - Draw!';
        } else {
            const winnerText = data.winner === humanColor ? 'You win!' : 'Computer wins!';
            statusDiv.textContent = `Game Over - ${winnerText}`;
        }
        statusDiv.style.background = '#ffd700';
    } else if (data.in_check) {
        statusDiv.textContent = `${data.current_player === humanColor ? 'You are' : 'Computer is'} in check!`;
        statusDiv.style.background = '#ffcccb';
    } else {
        statusDiv.textContent = data.current_player === humanColor ? 'Your turn' : 'Computer is thinking...';
        statusDiv.style.background = '#f0f0f0';
    }
}

function addMoveToHistory(player, from, to) {
    const moveEntry = document.createElement('div');
    moveEntry.className = 'move-entry';
    moveEntry.textContent = `${moveHistory.length + 1}. ${player}: ${from} → ${to}`;
    moveHistoryDiv.appendChild(moveEntry);
    moveHistoryDiv.scrollTop = moveHistoryDiv.scrollHeight;
    moveHistory.push({ player, from, to });
}

function positionToString(row, col) {
    return String.fromCharCode(97 + col) + (8 - row);
}
