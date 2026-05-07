import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga 1v1 Arena", layout="wide")

st.markdown("""
    <style>
    .stApp { display: flex; justify-content: center; background-color: #0e1117; }
    iframe { display: block; margin: auto; border-radius: 15px; box-shadow: 0 0 30px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<div id="main-container" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 20px; font-family: 'Arial', sans-serif; color: white; width: 740px; margin: auto; border: 2px solid #333;">
    
    <div id="menu" style="text-align: center; width: 100%;">
        <h1 style="font-size: 36px; color: #f1c40f; text-shadow: 2px 2px #000;">BUNDESLIGA 1v1</h1>
        <div style="display: flex; justify-content: space-around; gap: 15px; margin-bottom: 20px;">
            <div style="background: #222; padding: 15px; border-radius: 12px; border: 2px solid #3498db; flex: 1;">
                <h4 style="color: #3498db; margin: 0 0 10px 0;">Spieler 1 (WASD)</h4>
                <select id="p1Select" style="padding: 8px; width: 100%;"><option value="HSV">HSV</option><option value="Werder">Werder</option><option value="Bayern">Bayern</option><option value="BVB">BVB</option></select>
            </div>
            <div style="background: #222; padding: 15px; border-radius: 12px; border: 2px solid #e74c3c; flex: 1;">
                <h4 style="color: #e74c3c; margin: 0 0 10px 0;">Spieler 2 (Pfeile)</h4>
                <select id="p2Select" style="padding: 8px; width: 100%;"><option value="Bayern">Bayern</option><option value="Werder">Werder</option><option value="HSV">HSV</option><option value="BVB">BVB</option></select>
            </div>
        </div>
        <button onclick="startGame()" style="padding: 12px 50px; font-size: 20px; background: #27ae60; color: white; border: none; border-radius: 30px; cursor: pointer; font-weight: bold;">ANPFIFF!</button>
    </div>

    <div id="game-area" style="display: none; width: 100%; text-align: center; position: relative;">
        <div id="goal-overlay" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 100px; font-weight: 900; color: #f1c40f; text-shadow: 5px 5px #000; z-index: 10;">GOAL!</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <button onclick="showMenu()" style="background: #444; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer;">Menü</button>
            <div style="font-size: 24px; font-weight: bold; background: #000; padding: 5px 20px; border-radius: 8px;">
                <span id="p1-display"></span> <span id="score-display">0 : 0</span> <span id="p2-display"></span>
            </div>
            <div id="timer-display" style="color: #0f0; font-family: monospace; font-size: 20px;">120s</div>
        </div>
        <canvas id="gameCanvas" width="700" height="400" style="border: 4px solid #444; border-radius: 10px; background: #1a5e1a;"></canvas>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const goalOverlay = document.getElementById("goal-overlay");
const teams = { "HSV": "#3498db", "Werder": "#2ecc71", "Bayern": "#e74c3c", "BVB": "#f1c40f" };

let gameActive = false, isPaused = false, timeLeft = 120, score1 = 0, score2 = 0, timerInterval, frameCount = 0;
const gravity = 0.38, keys = {};
let ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
let p1 = { x: 80, y: 350, w: 32, h: 48, dy: 0, jump: false, color: "", name: "" };
let p2 = { x: 588, y: 350, w: 32, h: 48, dy: 0, jump: false, color: "", name: "" };

// Zuschauer generieren
const fans = [];
for(let i=0; i<20; i++) {
    fans.push({ x: 30 + i*34, y: 180 + Math.random()*40, color: Object.values(teams)[i%4], offset: Math.random()*Math.PI*2 });
}

window.addEventListener("keydown", e => { if(gameActive) { keys[e.code] = true; if(["ArrowUp","ArrowLeft","ArrowRight","ArrowDown"].includes(e.code)) e.preventDefault(); }});
window.addEventListener("keyup", e => keys[e.code] = false);

function startGame() {
    p1.name = document.getElementById("p1Select").value; p1.color = teams[p1.name];
    p2.name = document.getElementById("p2Select").value; p2.color = teams[p2.name];
    document.getElementById("p1-display").innerText = p1.name; document.getElementById("p1-display").style.color = p1.color;
    document.getElementById("p2-display").innerText = p2.name; document.getElementById("p2-display").style.color = p2.color;
    document.getElementById("menu").style.display = "none"; document.getElementById("game-area").style.display = "block";
    gameActive = true; score1 = 0; score2 = 0; timeLeft = 120; resetRound(); startTimer(); update();
}

function startTimer() {
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => { if(!isPaused && gameActive) { if(timeLeft > 0) { timeLeft--; document.getElementById("timer-display").innerText = timeLeft + "s"; } else endGame(); } }, 1000);
}

function showMenu() { gameActive = false; clearInterval(timerInterval); document.getElementById("menu").style.display = "block"; document.getElementById("game-area").style.display = "none"; }

function resetRound() { p1.x = 80; p1.y = 350; p1.dy = 0; p2.x = 588; p2.y = 350; p2.dy = 0; ball.x = 350; ball.y = 40; ball.dx = (Math.random()-0.5)*4; ball.dy = 0; isPaused = false; goalOverlay.style.display = "none"; }

function handleGoal(winner) { if (isPaused) return; isPaused = true; goalOverlay.style.display = "block"; if(winner === 1) score1++; else score2++; document.getElementById("score-display").innerText = score1 + " : " + score2; setTimeout(resetRound, 2000); }

function resolveCollision(p, b) {
    let closestX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closestY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    let distanceX = b.x - closestX;
    let distanceY = b.y - closestY;
    let distanceSquared = (distanceX * distanceX) + (distanceY * distanceY);

    if (distanceSquared < (b.radius * b.radius)) {
        // Kick Logik: Wo wird der Spieler getroffen?
        if (Math.abs(distanceX) > Math.abs(distanceY)) {
            b.dx = distanceX > 0 ? 5 : -5; // Seitlicher Abpraller
            b.dy = -4; 
        } else {
            b.dy = distanceY > 0 ? 4 : -9; // Kopfball oder Treffer von unten
        }
        b.x += b.dx; b.y += b.dy; // Aus der Hitbox schieben
    }
}

function update() {
    if (!gameActive) return;
    if (!isPaused) {
        if (keys['KeyA'] && p1.x > 0) p1.x -= 4.5; if (keys['KeyD'] && p1.x < 668) p1.x += 4.5;
        if (keys['KeyW'] && !p1.jump) { p1.dy = -10; p1.jump = true; }
        if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 4.5; if (keys['ArrowRight'] && p2.x < 668) p2.x += 4.5;
        if (keys['ArrowUp'] && !p2.jump) { p2.dy = -10; p2.jump = true; }

        [p1, p2].forEach(p => { p.y += p.dy; if (p.y < 350) p.dy += gravity; else { p.y = 350; p.dy = 0; p.jump = false; } });

        ball.x += ball.dx; ball.y += ball.dy; ball.dy += gravity * 0.5; ball.dx *= 0.99;
        if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.7; }
        if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.7; ball.x = ball.x < ball.radius ? ball.radius : 700 - ball.radius; }
        if (ball.y > 390) { ball.y = 390; ball.dy *= -0.5; ball.dx *= 0.9; }

        if (ball.y > 270 && ball.y < 295) { if (ball.x < 35) { ball.dy = -5; ball.dx = 5; } if (ball.x > 665) { ball.dy = -5; ball.dx = -5; } }
        if (ball.y > 280) { if (ball.x < 15) handleGoal(2); if (ball.x > 685) handleGoal(1); }
        [p1, p2].forEach(p => resolveCollision(p, ball));
    }
    frameCount++; draw(); requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0,0,700,400);
    // Himmel & Tribüne
    ctx.fillStyle = "#16213e"; ctx.fillRect(0, 0, 700, 250);
    // Fans zeichnen
    fans.forEach(f => {
        let bounce = Math.sin(frameCount * 0.1 + f.offset) * 3;
        ctx.fillStyle = f.color; ctx.fillRect(f.x, f.y + bounce, 12, 15); // Körper
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(f.x + 2, f.y - 6 + bounce, 8, 8); // Kopf
    });
    // Rasen & Linien
    ctx.fillStyle = "#2e7d32"; ctx.fillRect(0, 250, 700, 150);
    ctx.strokeStyle = "rgba(255,255,255,0.2)"; ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 680, 380); ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();
    // Tore
    ctx.strokeStyle = "white"; ctx.lineWidth = 6;
    ctx.strokeRect(-2, 280, 22, 120); ctx.strokeRect(680, 280, 22, 120);
    // Spieler
    [p1, p2].forEach(p => {
        ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(p.x + 4, p.y - 14, 24, 14);
        ctx.strokeStyle = "#000"; ctx.lineWidth = 1; ctx.strokeRect(p.x, p.y, p.w, p.h);
    });
    // Ball
    ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = "black"; ctx.stroke();
}

function endGame() { gameActive = false; alert("SPIEL ENDE! Endstand: " + score1 + " : " + score2); showMenu(); }
</script>
"""

components.html(game_html, height=720, scrolling=False)
