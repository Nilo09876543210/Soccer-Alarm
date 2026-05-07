import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga Arena 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { display: flex; justify-content: center; background-color: #0e1117; }
    iframe { display: block; margin: auto; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<div id="main-container" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 25px; font-family: 'Arial Black', sans-serif; color: white; width: 750px; margin: auto; border: 3px solid #444;">
    
    <div id="menu" style="text-align: center; width: 100%;">
        <h1 style="font-size: 40px; color: #f1c40f; text-shadow: 3px 3px #000; margin-bottom: 5px;">BUNDESLIGA 1v1</h1>
        <p style="color: #888; font-family: Arial; margin-bottom: 25px;">Official 2026 Team Edition</p>
        
        <div style="display: flex; justify-content: space-around; gap: 15px; margin-bottom: 30px;">
            <div style="background: #222; padding: 15px; border-radius: 15px; border: 2px solid #3498db; flex: 1;">
                <h3 style="color: #3498db; font-size: 16px;">HEIM (WASD)</h3>
                <select id="p1Select" style="padding: 10px; width: 100%; cursor: pointer;"></select>
            </div>
            <div style="background: #222; padding: 15px; border-radius: 15px; border: 2px solid #e74c3c; flex: 1;">
                <h3 style="color: #e74c3c; font-size: 16px;">GAST (Pfeile)</h3>
                <select id="p2Select" style="padding: 10px; width: 100%; cursor: pointer;"></select>
            </div>
        </div>
        <button onclick="startGame()" style="padding: 20px 70px; font-size: 22px; background: #27ae60; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">ANPFIFF</button>
    </div>

    <div id="game-area" style="display: none; width: 100%; text-align: center; position: relative;">
        <div id="goal-overlay" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 100px; font-weight: 900; color: #f1c40f; text-shadow: 6px 6px #000; z-index: 100;">GOAL!</div>
        
        <div id="win-overlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); flex-direction: column; justify-content: center; align-items: center; z-index: 200; border-radius: 10px;">
            <h2 style="color: #f1c40f; font-size: 24px;">🏆 ENDSTAND 🏆</h2>
            <h1 id="winner-name" style="font-size: 55px; margin: 15px 0;">TEAM</h1>
            <button onclick="showMenu()" style="padding: 12px 35px; background: #fff; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">HAUPTMENÜ</button>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 22px; font-weight: bold; background: #000; padding: 10px 25px; border-radius: 10px; border: 1px solid #333;">
                <span id="p1-display"></span> <span id="score-display" style="color: #f1c40f; margin: 0 10px;">0 : 0</span> <span id="p2-display"></span>
            </div>
            <div id="timer-display" style="font-family: monospace; font-size: 30px; color: #0f0;">90s</div>
        </div>
        <canvas id="gameCanvas" width="700" height="400" style="border: 4px solid #333; border-radius: 10px; background: #1a5e1a;"></canvas>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const goalOverlay = document.getElementById("goal-overlay");
const winOverlay = document.getElementById("win-overlay");

const teams = { 
    "Bayern": { main: "#dc052d", sec: "#ffffff", shorts: "#dc052d", pat: "stripes-h" },
    "BVB": { main: "#fff200", sec: "#000000", shorts: "#000000", pat: "stripes-v" },
    "Leverkusen": { main: "#000000", sec: "#e32221", shorts: "#000000", pat: "plain" },
    "RB Leipzig": { main: "#ffffff", sec: "#dd013f", shorts: "#dd013f", pat: "plain" },
    "Eintracht": { main: "#e32219", sec: "#000000", shorts: "#000000", pat: "stripes-v" },
    "Werder": { main: "#1d903d", sec: "#ffffff", shorts: "#ffffff", pat: "plain" },
    "St. Pauli": { main: "#634836", sec: "#ffffff", shorts: "#634836", pat: "plain" },
    "Freiburg": { main: "#e32221", sec: "#ffffff", shorts: "#ffffff", pat: "stripes-v" },
    "HSV": { main: "#005ca9", sec: "#ffffff", shorts: "#ffffff", pat: "plain" }
};

// Dropdowns füllen
const p1Sel = document.getElementById("p1Select");
const p2Sel = document.getElementById("p2Select");
Object.keys(teams).forEach(t => {
    p1Sel.add(new Option(t, t));
    p2Sel.add(new Option(t, t));
});
p2Sel.value = "Leverkusen";

let gameActive = false, isPaused = false, timeLeft = 90, score1 = 0, score2 = 0, timerInterval, frameCount = 0;
const gravity = 0.4, keys = {};
let ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
let p1 = { x: 80, y: 350, w: 34, h: 50, dy: 0, jump: false, team: "Bayern" };
let p2 = { x: 588, y: 350, w: 34, h: 50, dy: 0, jump: false, team: "Leverkusen" };

const fans = [];
for(let r=0; r<3; r++) { for(let i=0; i<22; i++) { fans.push({ x: 30 + i*31, y: 160 + r*25, color: Object.values(teams)[(i+r)%9].main, offset: i * 0.4 }); } }

window.addEventListener("keydown", e => { if(gameActive) { keys[e.code] = true; if(["ArrowUp","ArrowLeft","ArrowRight","ArrowDown"].includes(e.code)) e.preventDefault(); }});
window.addEventListener("keyup", e => keys[e.code] = false);

function startGame() {
    p1.team = p1Sel.value; p2.team = p2Sel.value;
    document.getElementById("p1-display").innerText = p1.team; document.getElementById("p1-display").style.color = teams[p1.team].main;
    document.getElementById("p2-display").innerText = p2.team; document.getElementById("p2-display").style.color = teams[p2.team].main;
    document.getElementById("menu").style.display = "none"; document.getElementById("game-area").style.display = "block";
    winOverlay.style.display = "none";
    gameActive = true; score1 = 0; score2 = 0; timeLeft = 90; resetRound(); startTimer(); update();
}

function startTimer() {
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => { if(!isPaused && gameActive) { if(timeLeft > 0) { timeLeft--; document.getElementById("timer-display").innerText = timeLeft + "s"; } else endGame(); } }, 1000);
}

function showMenu() { gameActive = false; clearInterval(timerInterval); document.getElementById("menu").style.display = "block"; document.getElementById("game-area").style.display = "none"; }

function resetRound() { p1.x = 80; p1.y = 350; p1.dy = 0; p2.x = 588; p2.y = 350; p2.dy = 0; ball.x = 350; ball.y = 60; ball.dx = (Math.random()-0.5)*5; ball.dy = 0; isPaused = false; goalOverlay.style.display = "none"; }

function handleGoal(winner) { if (isPaused) return; isPaused = true; goalOverlay.style.display = "block"; if(winner === 1) score1++; else score2++; document.getElementById("score-display").innerText = score1 + " : " + score2; setTimeout(() => { if(gameActive) resetRound(); }, 2000); }

function resolveCollision(p, b) {
    let closestX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closestY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    let dX = b.x - closestX, dY = b.y - closestY;
    if ((dX * dX + dY * dY) < (b.radius * b.radius)) {
        if (Math.abs(dX) > Math.abs(dY)) { b.dx = dX > 0 ? 6.5 : -6.5; b.dy = -3; } else { b.dy = dY > 0 ? 5 : -11; }
        b.x += b.dx; b.y += b.dy;
    }
}

function update() {
    if (!gameActive) return;
    if (!isPaused) {
        if (keys['KeyA'] && p1.x > 0) p1.x -= 5; if (keys['KeyD'] && p1.x < 666) p1.x += 5;
        if (keys['KeyW'] && !p1.jump) { p1.dy = -11; p1.jump = true; }
        if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 5; if (keys['ArrowRight'] && p2.x < 666) p2.x += 5;
        if (keys['ArrowUp'] && !p2.jump) { p2.dy = -11; p2.jump = true; }
        [p1, p2].forEach(p => { p.y += p.dy; if (p.y < 350) p.dy += gravity; else { p.y = 350; p.dy = 0; p.jump = false; } });
        ball.x += ball.dx; ball.y += ball.dy; ball.dy += gravity * 0.5; ball.dx *= 0.985;
        if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.7; }
        if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.8; ball.x = ball.x < ball.radius ? ball.radius : 700 - ball.radius; }
        if (ball.y > 390) { ball.y = 390; ball.dy *= -0.5; ball.dx *= 0.9; }
        if (ball.y > 275 && ball.y < 300) { if (ball.x < 45) { ball.dy = -7; ball.dx = 7; } if (ball.x > 655) { ball.dy = -7; ball.dx = -7; } }
        if (ball.y > 280) { if (ball.x < 20) handleGoal(2); if (ball.x > 680) handleGoal(1); }
        [p1, p2].forEach(p => resolveCollision(p, ball));
    }
    frameCount++; draw(); requestAnimationFrame(update);
}

function drawPlayer(p, num) {
    const t = teams[p.team];
    // Trikot
    ctx.fillStyle = t.main; ctx.fillRect(p.x, p.y, p.w, p.h);
    // Design-Muster
    ctx.fillStyle = t.sec;
    if(t.pat === "stripes-v") { ctx.fillRect(p.x + 8, p.y, 4, p.h); ctx.fillRect(p.x + 22, p.y, 4, p.h); }
    else if(t.pat === "stripes-h") { ctx.fillRect(p.x, p.y + 10, p.w, 4); ctx.fillRect(p.x, p.y + 25, p.w, 4); }
    // Hosen
    ctx.fillStyle = t.shorts; ctx.fillRect(p.x, p.y + 32, p.w, 18);
    // Haut
    ctx.fillStyle = "#ffdbac"; ctx.fillRect(p.x + 5, p.y - 15, 24, 15);
    // Nummer
    ctx.fillStyle = (t.main === "#ffffff" || t.main === "#fff200") ? "#000" : "#fff";
    ctx.font = "bold 13px Arial"; ctx.fillText(num, p.x + 11, p.y + 22);
    // Outline
    ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.strokeRect(p.x, p.y, p.w, p.h);
}

function draw() {
    ctx.clearRect(0,0,700,400);
    ctx.fillStyle = "#16213e"; ctx.fillRect(0, 0, 700, 250);
    fans.forEach(f => {
        let wave = Math.sin(frameCount * 0.12 - f.offset) * 5;
        ctx.fillStyle = f.color; ctx.fillRect(f.x, f.y + wave, 12, 15);
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(f.x + 2, f.y - 7 + wave, 8, 8);
    });
    ctx.fillStyle = "#2e7d32"; ctx.fillRect(0, 250, 700, 150);
    ctx.strokeStyle = "rgba(255,255,255,0.2)"; ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 680, 380); ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();
    ctx.strokeStyle = "#fff"; ctx.lineWidth = 6; ctx.strokeRect(-5, 280, 25, 120); ctx.strokeRect(680, 280, 25, 120);
    
    drawPlayer(p1, "7");
    drawPlayer(p2, "10");

    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = "#000"; ctx.lineWidth = 1; ctx.stroke();
}

function endGame() {
    gameActive = false;
    let winner = score1 > score2 ? p1.team : (score2 > score1 ? p2.team : "REMIS");
    document.getElementById("winner-name").innerText = winner;
    document.getElementById("winner-name").style.color = (winner !== "REMIS") ? teams[winner].main : "#fff";
    winOverlay.style.display = "flex";
}
</script>
"""

components.html(game_html, height=750, scrolling=False)
