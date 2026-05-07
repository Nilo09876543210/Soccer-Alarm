import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Soccer 1v1 Deluxe", layout="centered")

st.title("⚽ Street Soccer JS")
st.markdown("### Spieler 1: WASD | Spieler 2: Pfeiltasten")

game_html = """
<div id="container" style="display: flex; flex-direction: column; align-items: center; background: #eee; padding: 20px; border-radius: 15px;">
    <div id="scoreboard" style="font-family: 'Courier New', monospace; font-size: 40px; font-weight: bold; margin-bottom: 10px;">
        <span style="color: blue;">P1</span> 
        <span id="score">0 : 0</span> 
        <span style="color: red;">P2</span>
    </div>
    <div style="font-size: 18px; margin-bottom: 10px;">Verbleibende Zeit: <span id="timer">120</span>s</div>
    
    <canvas id="gameCanvas" width="700" height="400" style="border:4px solid #333; background: #2e7d32; border-radius: 5px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);"></canvas>
    
    <p style="margin-top: 10px; color: #666;">Klicke ins Feld zum Starten!</p>
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

const gravity = 0.45;
const keys = {};

// Objekte
const ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 12 };
const p1 = { x: 80, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#0055ff" };
const p2 = { x: 580, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#ff2200" };

window.addEventListener("keydown", e => {
    keys[e.code] = true;
    if(["ArrowUp","ArrowDown","Space"].includes(e.code)) e.preventDefault();
});
window.addEventListener("keyup", e => keys[e.code] = false);

function resetBall() {
    ball.x = 350;
    ball.y = -20;
    ball.dx = (Math.random() - 0.5) * 5;
    ball.dy = 2;
}

function checkCollision(p, b) {
    // Einfache Kreis-Rechteck Kollision
    let closeX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closeY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    
    let distanceX = b.x - closeX;
    let distanceY = b.y - closeY;
    let distanceSquared = (distanceX * distanceX) + (distanceY * distanceY);
    
    return distanceSquared < (b.radius * b.radius);
}

function update() {
    if (gameOver) return;

    // Steuerung P1
    if (keys['KeyA'] && p1.x > 0) p1.x -= 6;
    if (keys['KeyD'] && p1.x < 320) p1.x += 6;
    if (keys['KeyW'] && !p1.jump) { p1.dy = -12; p1.jump = true; }

    // Steuerung P2
    if (keys['ArrowLeft'] && p2.x > 350) p2.x -= 6;
    if (keys['ArrowRight'] && p2.x < 665) p2.x += 6;
    if (keys['ArrowUp'] && !p2.jump) { p2.dy = -12; p2.jump = true; }

    // Spieler-Physik
    [p1, p2].forEach(p => {
        p.y += p.dy;
        if (p.y < 350) p.dy += gravity;
        else { p.y = 350; p.dy = 0; p.jump = false; }
    });

    // Ball-Physik
    ball.x += ball.dx;
    ball.y += ball.dy;
    ball.dy += gravity * 0.7;

    // Ball-Wand Kollision
    if (ball.x < ball.radius || ball.x > 700 - ball.radius) ball.dx *= -0.7;
    if (ball.y > 388) { ball.y = 388; ball.dy *= -0.6; }
    if (ball.y < 0) ball.dy *= -1;

    // Spieler-Ball Kontakt
    [p1, p2].forEach(p => {
        if (checkCollision(p, ball)) {
            // Kick-Effekt: Ball bekommt Schwung basierend auf Position zum Spieler
            ball.dy = -9;
            ball.dx = (ball.x - (p.x + p.w/2)) * 0.6;
            // Kleiner Extra-Schubs nach oben
            if (keys['KeyW'] || keys['ArrowUp']) ball.dy = -13;
        }
    });

    // Tor-Logik
    if (ball.x < 20 && ball.y > 280) { score2++; resetBall(); }
    if (ball.x > 680 && ball.y > 280) { score1++; resetBall(); }

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, 700, 400);

    // Rasen-Linien
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.strokeRect(350, 0, 1, 400);
    ctx.strokeRect(0, 390, 700, 10);

    // Tore zeichnen
    ctx.fillStyle = "white";
    ctx.fillRect(0, 280, 15, 120); // Tor links
    ctx.fillRect(685, 280, 15, 120); // Tor rechts

    // Spieler
    ctx.shadowBlur = 10;
    ctx.fillStyle = p1.color; ctx.shadowColor = p1.color;
    ctx.fillRect(p1.x, p1.y, p1.w, p1.h);
    
    ctx.fillStyle = p2.color; ctx.shadowColor = p2.color;
    ctx.fillRect(p2.x, p2.y, p2.w, p2.h);

    // Ball
    ctx.shadowBlur = 15; ctx.shadowColor = "white";
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2);
    ctx.fill();
    ctx.shadowBlur = 0;

    scoreEl.innerText = score1 + " : " + score2;
}

// Timer-Intervall
const gameTimer = setInterval(() => {
    if (timeLeft > 0) {
        timeLeft--;
        timerEl.innerText = timeLeft;
    } else {
        gameOver = true;
        clearInterval(gameTimer);
        alert("FINALE! Endstand " + score1 + ":" + score2);
        location.reload();
    }
}, 1000);

update();
</script>
"""

components.html(game_html, height=600)
