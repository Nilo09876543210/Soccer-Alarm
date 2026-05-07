import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Soccer Challenge", layout="centered")

st.title("⚽ 1-gegen-1 Meister-Cup")
st.write("Steuerung: Spieler 1 (WASD) | Spieler 2 (Pfeiltasten)")

# Das Spiel wird in einem HTML/JavaScript Block definiert
game_html = """
<canvas id="gameCanvas" width="700" height="400" style="border:2px solid #fff; background: #228B22;"></canvas>
<div id="ui" style="color: white; font-family: Arial; font-size: 20px; margin-top: 10px;">
    Zeit: <span id="timer">120</span>s | Score: <span id="score">0 : 0</span>
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

// Spieler & Ball Objekte
const ball = { x: 350, y: 50, dx: 0, dy: 2, radius: 10 };
const p1 = { x: 50, y: 350, w: 30, h: 50, dy: 0, jump: false };
const p2 = { x: 620, y: 350, w: 30, h: 50, dy: 0, jump: false };

const gravity = 0.5;
const keys = {};

window.addEventListener("keydown", e => keys[e.code] = true);
window.addEventListener("keyup", e => keys[e.code] = false);

function resetBall() {
    ball.x = 350;
    ball.y = 0; // Fällt von der Decke
    ball.dx = (Math.random() - 0.5) * 4;
    ball.dy = 2;
}

function update() {
    if (gameOver) return;

    // Zeit-Logik
    if (Math.random() < 0.016) { // Ca. jede Sekunde (bei ~60fps)
        // Einfacherer Timer-Mechanismus
    }

    // Spieler 1 (WASD)
    if (keys['KeyA'] && p1.x > 0) p1.x -= 5;
    if (keys['KeyD'] && p1.x < 300) p1.x += 5;
    if (keys['KeyW'] && !p1.jump) { p1.dy = -10; p1.jump = true; }

    // Spieler 2 (Arrows)
    if (keys['ArrowLeft'] && p2.x > 400) p2.x -= 5;
    if (keys['ArrowRight'] && p2.x < 670) p2.x += 5;
    if (keys['ArrowUp'] && !p2.jump) { p2.dy = -10; p2.jump = true; }

    // Physik für Spieler
    [p1, p2].forEach(p => {
        p.y += p.dy;
        if (p.y < 350) p.dy += gravity;
        else { p.y = 350; p.dy = 0; p.jump = false; }
    });

    // Ball-Physik
    ball.x += ball.dx;
    ball.y += ball.dy;
    ball.dy += gravity * 0.5;

    // Kollision Wand/Boden
    if (ball.x < 0 || ball.x > 700) ball.dx *= -1;
    if (ball.y > 390) { ball.y = 390; ball.dy *= -0.7; }

    // Tor-Logik (Bereiche links und rechts)
    if (ball.x < 15 && ball.y > 300) { score2++; resetBall(); }
    if (ball.x > 685 && ball.y > 300) { score1++; resetBall(); }

    // Spieler-Ball Kollision (Simpel)
    [p1, p2].forEach(p => {
        if (ball.x > p.x && ball.x < p.x + p.w && ball.y > p.y && ball.y < p.y + p.h) {
            ball.dy = -8;
            ball.dx = (ball.x - (p.x + p.w/2)) * 0.5;
        }
    });

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, 700, 400);

    // Tore zeichnen
    ctx.strokeStyle = "white";
    ctx.strokeRect(0, 300, 20, 100);
    ctx.strokeRect(680, 300, 20, 100);

    // Spieler
    ctx.fillStyle = "blue"; ctx.fillRect(p1.x, p1.y, p1.w, p1.h);
    ctx.fillStyle = "red"; ctx.fillRect(p2.x, p2.y, p2.w, p2.h);

    // Ball
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2);
    ctx.fill();

    scoreEl.innerText = score1 + " : " + score2;
}

// Timer Intervall
setInterval(() => {
    if (timeLeft > 0) {
        timeLeft--;
        timerEl.innerText = timeLeft;
    } else {
        gameOver = true;
        alert("Spiel vorbei! Endstand: " + score1 + ":" + score2);
        location.reload();
    }
}, 1000);

update();
</script>
"""

components.html(game_html, height=500)
