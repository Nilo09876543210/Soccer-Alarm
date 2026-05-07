import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga Arena 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { display: flex; justify-content: center; background-color: #0e1117; }
    iframe { display: block; margin: auto; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.7); }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<div id="main-container" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 25px; font-family: 'Segoe UI', Arial, sans-serif; color: white; width: 750px; margin: auto; border: 3px solid #444;">
    
    <div id="menu" style="text-align: center; width: 100%;">
        <h1 style="font-size: 45px; color: #f1c40f; text-shadow: 3px 3px #000; margin-bottom: 10px;">BUNDESLIGA ULTIMATE</h1>
        <p style="color: #aaa;">Wähle dein Team und dominiere die Arena</p>
        <div style="display: flex; justify-content: space-around; gap: 20px; margin: 30px 0;">
            <div style="background: #222; padding: 20px; border-radius: 15px; border: 2px solid #3498db; flex: 1;">
                <h3 style="color: #3498db;">HEIM (WASD)</h3>
                <select id="p1Select" style="padding: 10px; width: 100%; border-radius: 5px;"><option value="HSV">HSV</option><option value="Werder">Werder</option><option value="Bayern">Bayern</option><option value="BVB">BVB</option></select>
            </div>
            <div style="background: #222; padding: 20px; border-radius: 15px; border: 2px solid #e74c3c; flex: 1;">
                <h3 style="color: #e74c3c;">GAST (Pfeile)</h3>
                <select id="p2Select" style="padding: 10px; width: 100%; border-radius: 5px;"><option value="Bayern">Bayern</option><option value="Werder">Werder</option><option value="HSV">HSV</option><option value="BVB">BVB</option></select>
            </div>
        </div>
        <button onclick="startGame()" style="padding: 18px 60px; font-size: 24px; background: #27ae60; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; transition: 0.3s; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">SPIEL STARTEN</button>
    </div>

    <div id="game-area" style="display: none; width: 100%; text-align: center; position: relative;">
        <!-- Overlays -->
        <div id="goal-overlay" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 110px; font-weight: 900; color: #f1c40f; text-shadow: 6px 6px #000; z-index: 100;">GOAL!</div>
        
        <div id="win-overlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); flex-direction: column; justify-content: center; align-items: center; z-index: 200; border-radius: 10px;">
            <h2 style="color: #f1c40f; font-size: 30px;">🏆 MEISTER 2026 🏆</h2>
            <h1 id="winner-name" style="font-size: 60px; margin: 10px 0;">TEAM</h1>
            <button onclick="showMenu()" style="margin-top: 20px; padding: 10px 30px; background: #fff; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">ZUM HAUPTMENÜ</button>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div style="font-size: 26px; font-weight: bold; background: #000; padding: 8px 25px; border-radius: 10px; border: 1px solid #333;">
                <span id="p1-display"></span> <span id="score-display" style="color: #f1c40f;">0 : 0</span> <span id="p2-display"></span>
            </div>
            <div id="timer-display" style="font-family: 'Courier New', monospace; font-size: 28px; color: #0f0;">120s</div>
        </div>
        <canvas id="gameCanvas" width="700" height="400" style="border: 5px solid #333; border-radius: 10px; background: #1a5e1a;"></canvas>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const goalOverlay = document.getElementById("goal-overlay");
const winOverlay = document.getElementById("win-overlay");
const teams = { "HSV": "#3498db", "Werder": "#2ecc71", "Bayern": "#e74c3c", "BVB": "#f1c40f" };

let gameActive = false, isPaused = false, timeLeft = 120, score1 = 0, score2 = 0, timerInterval, frameCount = 0;
const gravity = 0.4, keys = {};
let ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
let p1 = { x: 80, y: 350, w: 32, h: 48, dy: 0, jump: false, color: "", name: "" };
let p2 = { x: 588, y: 350, w: 32, h: 48, dy: 0, jump: false, color: "", name: "" };

// 60 Zuschauer in 3 Reihen
const fans = [];
for(let r=0; r<3; r++) {
    for(let i=0; i<20; i++) {
        fans.push({ 
            x: 40 + i*33, 
            y: 160 + r*25, 
            color: Object.values(teams)[(i+r)%4], 
            offset: i * 0.3 + r 
        });
    }
}

window.addEventListener("keydown", e => { if(gameActive) { keys[e.code] = true; if(["ArrowUp","ArrowLeft","ArrowRight","ArrowDown"].includes(e.code)) e.preventDefault(); }});
window.addEventListener("keyup", e => keys[e.code] = false);

function startGame() {
    p1.name = document.getElementById("p1Select").value; p1.color = teams[p1.name];
    p2.name = document.getElementById("p2Select").value; p2.color = teams[p2.name];
    document.getElementById("p1-display").innerText = p1.name; document.getElementById("p1-display").style.color = p1.color;
    document.getElementById("p2-display").innerText = p2.name; document.getElementById("p2-display").style.color = p2.color;
    document.getElementById("menu").style.display = "none"; document.getElementById("game-area").style.display = "block";
    winOverlay.style.display = "none";
    gameActive = true; score1 = 0; score2 = 0; timeLeft = 90; resetRound(); startTimer(); update();
}

function startTimer() {
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => { 
        if(!isPaused && gameActive) { 
            if(timeLeft > 0) { timeLeft--; document.getElementById("timer-display").innerText = timeLeft + "s"; } 
            else endGame(); 
        } 
    }, 1000);
}

function showMenu() { gameActive = false; clearInterval(timerInterval); document.getElementById("menu").style.display = "block"; document.getElementById("game-area").style.display = "none"; }

function resetRound() { p1.x = 80; p1.y = 350; p1.dy = 0; p2.x = 588; p2.y = 350; p2.dy = 0; ball.x = 350; ball.y = 60; ball.dx = (Math.random()-0.5)*4; ball.dy = 0; isPaused = false; goalOverlay.style.display = "none"; }

function handleGoal(winner) { 
    if (isPaused) return; 
    isPaused = true; 
    goalOverlay.style.display = "block"; 
    if(winner === 1) score1++; else score2++; 
    document.getElementById("score-display").innerText = score1 + " : " + score2; 
    setTimeout(() => { if(gameActive) resetRound(); }, 2000); 
}

function resolveCollision(p, b) {
    let closestX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closestY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    let dX = b.x - closestX;
    let dY = b.y - closestY;
    if ((dX * dX + dY * dY) < (b.radius * b.radius)) {
        if (Math.abs(dX) > Math.abs(dY)) { b.dx = dX > 0 ? 6 : -6; b.dy = -3; } 
        else { b.dy = dY > 0 ? 4 : -10; }
        b.x += b.dx; b.y += b.dy;
    }
}

function update() {
    if (!gameActive) return;
    if (!isPaused) {
        if (keys['KeyA'] && p1.x > 0) p1.x -= 5; if (keys['KeyD'] && p1.x < 668) p1.x += 5;
        if (keys['KeyW'] && !p1.jump) { p1.dy = -11; p1.jump = true; }
        if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 5; if (keys['ArrowRight'] && p2.x < 668) p2.x += 5;
        if (keys['ArrowUp'] && !p2.jump) { p2.dy = -11; p2.jump = true; }

        [p1, p2].forEach(p => { p.y += p.dy; if (p.y < 350) p.dy += gravity; else { p.y = 350; p.dy = 0; p.jump = false; } });
        ball.x += ball.dx; ball.y += ball.dy; ball.dy += gravity * 0.5; ball.dx *= 0.985;
        if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.7; }
        if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.8; ball.x = ball.x < ball.radius ? ball.radius : 700 - ball.radius; }
        if (ball.y > 390) { ball.y = 390; ball.dy *= -0.5; ball.dx *= 0.9; }
        if (ball.y > 275 && ball.y < 300) { if (ball.x < 40) { ball.dy = -6; ball.dx = 6; } if (ball.x > 660) { ball.dy = -6; ball.dx = -6; } }
        if (ball.y > 280) { if (ball.x < 15) handleGoal(2); if (ball.x > 685) handleGoal(1); }
        [p1, p2].forEach(p => resolveCollision(p, ball));
    }
    frameCount++; draw(); requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0,0,700,400);
    // Background
    ctx.fillStyle = "#16213e"; ctx.fillRect(0, 0, 700, 250);
    // Fans mit Welle
    fans.forEach(f => {
        let wave = Math.sin(frameCount * 0.1 - f.offset) * 6;
        ctx.fillStyle = f.color; ctx.fillRect(f.x, f.y + wave, 12, 15);
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(f.x + 2, f.y - 7 + wave, 8, 8);
    });
    // Pitch
    ctx.fillStyle = "#2e7d32"; ctx.fillRect(0, 250, 700, 150);
    ctx.strokeStyle = "rgba(255,255,255,0.2)"; ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 680, 380); ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();
    // Goals
    ctx.strokeStyle = "white"; ctx.lineWidth = 6;
    ctx.strokeRect(-5, 280, 25, 120); ctx.strokeRect(680, 280, 25, 120);
    // Players
    [p1, p2].forEach(p => {
        ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(p.x + 4, p.y - 14, 24, 14);
        ctx.strokeStyle = "#000"; ctx.strokeRect(p.x, p.y, p.w, p.h);
    });
    // Ball
    ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = "black"; ctx.stroke();
}

function endGame() {
    gameActive = false;
    let winner = score1 > score2 ? p1.name : (score2 > score1 ? p2.name : "UNENTSCHIEDEN");
    let winColor = score1 > score2 ? p1.color : (score2 > score1 ? p2.color : "#fff");
    document.getElementById("winner-name").innerText = winner;
    document.getElementById("winner-name").style.color = winColor;
    winOverlay.style.display = "flex";
}
</script>
"""

components.html(game_html, height=750, scrolling=False)
