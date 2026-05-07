import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Soccer 1v1 Pro", layout="centered")

st.title("⚽ Street Soccer: Pro Edition")
st.markdown("### Steuerung: Spieler 1 (WASD) | Spieler 2 (Pfeiltasten)")

game_html = """
<div id="container" style="display: flex; flex-direction: column; align-items: center; background: #333; padding: 20px; border-radius: 15px; color: white;">
    <div id="scoreboard" style="font-family: 'Arial Black', sans-serif; font-size: 45px; margin-bottom: 10px;">
        <span style="color: #3498db;">P1</span> 
        <span id="score">0 : 0</span> 
        <span style="color: #e74c3c;">P2</span>
    </div>
    <div style="font-size: 18px; margin-bottom: 10px;">⏱ <span id="timer">120</span>s</div>
    
    <canvas id="gameCanvas" width="700" height="400" style="border:5px solid #555; background: #1a5e1a; cursor: none;"></canvas>
    
    <p style="margin-top: 15px; color: #aaa;">Tipp: Die Latte ist massiv! Der Ball muss unten rein.</p>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const timerEl = document.getElementById("timer");
const scoreEl = document.getElementById("score");

let timeLeft = 120;
let score1 = 0;
let score2 = 0;
let gameOver = false;

const gravity = 0.4;
const friction = 0.98;
const keys = {};

// Objekte
const ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
const p1 = { startX: 60, startY: 350, x: 60, y: 350, w: 30, h: 50, dy: 0, jump: false, color: "#3498db" };
const p2 = { startX: 610, startY: 350, x: 610, y: 350, w: 30, h: 50, dy: 0, jump: false, color: "#e74c3c" };

window.addEventListener("keydown", e => {
    keys[e.code] = true;
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)) e.preventDefault();
});
window.addEventListener("keyup", e => keys[e.code] = false);

function resetRound() {
    // Spieler zurücksetzen
    p1.x = p1.startX; p1.y = p1.startY; p1.dy = 0;
    p2.x = p2.startX; p2.y = p2.startY; p2.dy = 0;
    // Ball in der Mitte von oben
    ball.x = 350; ball.y = 20; ball.dx = 0; ball.dy = 0;
}

function checkCollision(p, b) {
    let closeX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closeY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    let dX = b.x - closeX;
    let dY = b.y - closeY;
    return (dX * dX + dY * dY) < (b.radius * b.radius);
}

function update() {
    if (gameOver) return;

    // Bewegung P1 (Frei auf dem Feld)
    if (keys['KeyA'] && p1.x > 0) p1.x -= 6;
    if (keys['KeyD'] && p1.x < 670) p1.x += 6;
    if (keys['KeyW'] && !p1.jump) { p1.dy = -11; p1.jump = true; }

    // Bewegung P2 (Frei auf dem Feld)
    if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 6;
    if (keys['ArrowRight'] && p2.x < 670) p2.x += 6;
    if (keys['ArrowUp'] && !p2.jump) { p2.dy = -11; p2.jump = true; }

    // Physik Spieler
    [p1, p2].forEach(p => {
        p.y += p.dy;
        if (p.y < 350) p.dy += gravity;
        else { p.y = 350; p.dy = 0; p.jump = false; }
    });

    // Physik Ball
    ball.x += ball.dx;
    ball.y += ball.dy;
    ball.dy += gravity * 0.6;
    ball.dx *= 0.99; // Luftwiderstand

    // Begrenzungen (Decke & Seitenwände)
    if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.8; }
    if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.8; }
    if (ball.y > 390) { ball.y = 390; ball.dy *= -0.6; ball.dx *= 0.95; }

    // Torlatten-Abpraller (Die Tore gehen bis Höhe 280)
    // Wenn Ball gegen die Pfosten/Latte knallt (oben bei 280px)
    if (ball.y < 285 && ball.y > 275) {
        if (ball.x < 30 || ball.x > 670) { ball.dy *= -0.8; ball.y = 274; }
    }

    // Tor-Logik (Nur wenn unter der Latte und ganz am Rand)
    if (ball.y > 280) {
        if (ball.x < 15) { score2++; resetRound(); }
        if (ball.x > 685) { score1++; resetRound(); }
    }

    // Spieler-Ball Kontakt
    [p1, p2].forEach(p => {
        if (checkCollision(p, ball)) {
            ball.dy = -8;
            ball.dx = (ball.x - (p.x + p.w/2)) * 0.7;
        }
    });

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, 700, 400);

    // Feldmarkierungen
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(350, 200, 50, 0, Math.PI*2); ctx.stroke();
    ctx.moveTo(350, 0); ctx.lineTo(350, 400); ctx.stroke();

    // Tore (Gehäuse)
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 280, 5, 120); // Pfosten links
    ctx.fillRect(0, 280, 25, 5);   // Latte links
    ctx.fillRect(695, 280, 5, 120); // Pfosten rechts
    ctx.fillRect(675, 280, 25, 5);  // Latte rechts

    // Spieler
    ctx.fillStyle = p1.color; ctx.fillRect(p1.x, p1.y, p1.w, p1.h);
    ctx.fillStyle = p2.color; ctx.fillRect(p2.x, p2.y, p2.w, p2.h);

    // Ball
    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2);
    ctx.fill();

    scoreEl.innerText = score1 + " : " + score2;
}

const gameTimer = setInterval(() => {
    if (timeLeft > 0) {
        timeLeft--;
        timerEl.innerText = timeLeft;
    } else {
        gameOver = true;
        clearInterval(gameTimer);
        alert("SPIEL ENDE! " + score1 + ":" + score2);
        location.reload();
    }
}, 1000);

update();
</script>
"""

components.html(game_html, height=600)
