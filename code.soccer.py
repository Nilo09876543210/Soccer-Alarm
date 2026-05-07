import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga 1v1 Ultimate", layout="wide") # Layout auf wide für mehr Platz

# CSS für Zentrierung in Streamlit
st.markdown("""
    <style>
    .stApp {
        display: flex;
        justify-content: center;
    }
    iframe {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

game_html = """
<div id="main-container" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 20px; font-family: 'Arial', sans-serif; color: white; width: 750px; margin: auto; box-shadow: 0 10px 50px rgba(0,0,0,0.8); border: 2px solid #333;">
    
    <!-- STARTMENÜ -->
    <div id="menu" style="text-align: center; width: 100%;">
        <h1 style="font-size: 40px; color: #f1c40f; text-shadow: 2px 2px #000; margin-bottom: 30px;">BUNDESLIGA 1v1</h1>
        <div style="display: flex; justify-content: space-around; gap: 20px;">
            <div style="background: #222; padding: 20px; border-radius: 15px; border: 2px solid #3498db; flex: 1;">
                <h3 style="color: #3498db;">HSV (WASD)</h3>
                <select id="p1Select" style="padding: 10px; width: 100%; border-radius: 5px;">
                    <option value="HSV">HSV (Blau)</option>
                    <option value="Werder">Werder (Grün)</option>
                    <option value="Bayern">Bayern (Rot)</option>
                    <option value="BVB">BVB (Gelb)</option>
                </select>
            </div>
            <div style="background: #222; padding: 20px; border-radius: 15px; border: 2px solid #e74c3c; flex: 1;">
                <h3 style="color: #e74c3c;">Gegner (Pfeile)</h3>
                <select id="p2Select" style="padding: 10px; width: 100%; border-radius: 5px;">
                    <option value="Bayern">Bayern (Rot)</option>
                    <option value="Werder">Werder (Grün)</option>
                    <option value="HSV">HSV (Blau)</option>
                    <option value="BVB">BVB (Gelb)</option>
                </select>
            </div>
        </div>
        <button onclick="startGame()" style="margin-top: 40px; padding: 15px 60px; font-size: 24px; background: #27ae60; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; box-shadow: 0 5px 15px rgba(39, 174, 96, 0.4);">ANPFIFF!</button>
    </div>

    <!-- SPIELBEREICH -->
    <div id="game-area" style="display: none; width: 100%; text-align: center; position: relative;">
        <div id="goal-overlay" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 100px; font-weight: 900; color: #f1c40f; text-shadow: 5px 5px #000; z-index: 10; pointer-events: none;">GOAL!</div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 15px;">
            <button onclick="showMenu()" style="background: #444; color: white; border: 1px solid #666; padding: 8px 15px; border-radius: 5px; cursor: pointer;">Home</button>
            <div style="font-size: 24px; font-weight: bold; font-family: 'Courier New', Courier, monospace;">
                <span id="p1-name-display">P1</span> 
                <span id="score-display" style="background:#000; padding: 5px 20px; border-radius: 10px; border: 1px solid #444; margin: 0 15px;">0 : 0</span> 
                <span id="p2-name-display">P2</span>
            </div>
            <div id="timer-display" style="font-family: monospace; font-size: 22px; color: #0f0; width: 70px; text-align: right;">120s</div>
        </div>
        
        <!-- Canvas fest auf 700px Breite gesetzt -->
        <canvas id="gameCanvas" width="700" height="400" style="border: 4px solid #555; border-radius: 10px; background: #1a5e1a; box-shadow: inset 0 0 50px rgba(0,0,0,0.5);"></canvas>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const goalOverlay = document.getElementById("goal-overlay");

const teams = { "HSV": "#3498db", "Werder": "#2ecc71", "Bayern": "#e74c3c", "BVB": "#f1c40f" };

let gameActive = false;
let isPaused = false;
let timeLeft = 120;
let score1 = 0;
let score2 = 0;
let timerInterval;

const gravity = 0.4;
const keys = {};

let ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
let p1 = { x: 80, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#3498db", name: "HSV" };
let p2 = { x: 585, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#e74c3c", name: "Bayern" };

window.addEventListener("keydown", e => { if(gameActive) { keys[e.code] = true; if(["ArrowUp","ArrowLeft","ArrowRight","ArrowDown","Space"].includes(e.code)) e.preventDefault(); }});
window.addEventListener("keyup", e => keys[e.code] = false);

function startGame() {
    p1.name = document.getElementById("p1Select").value;
    p1.color = teams[p1.name];
    p2.name = document.getElementById("p2Select").value;
    p2.color = teams[p2.name];
    
    document.getElementById("p1-name-display").innerText = p1.name;
    document.getElementById("p1-name-display").style.color = p1.color;
    document.getElementById("p2-name-display").innerText = p2.name;
    document.getElementById("p2-name-display").style.color = p2.color;

    document.getElementById("menu").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    
    gameActive = true;
    score1 = 0; score2 = 0; timeLeft = 120;
    document.getElementById("score-display").innerText = "0 : 0";
    resetRound();
    startTimer();
    update();
}

function startTimer() {
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if(!isPaused && gameActive) {
            if(timeLeft > 0) {
                timeLeft--;
                document.getElementById("timer-display").innerText = timeLeft + "s";
            } else { endGame(); }
        }
    }, 1000);
}

function showMenu() {
    gameActive = false;
    clearInterval(timerInterval);
    document.getElementById("menu").style.display = "block";
    document.getElementById("game-area").style.display = "none";
}

function resetRound() {
    p1.x = 80; p1.y = 350; p1.dy = 0;
    p2.x = 585; p2.y = 350; p2.dy = 0;
    ball.x = 350; ball.y = 50; ball.dx = (Math.random()-0.5)*4; ball.dy = 0;
    isPaused = false;
    goalOverlay.style.display = "none";
}

function handleGoal(winner) {
    if (isPaused) return;
    isPaused = true;
    goalOverlay.style.display = "block";
    if(winner === 1) score1++; else score2++;
    document.getElementById("score-display").innerText = score1 + " : " + score2;
    setTimeout(resetRound, 2000);
}

function resolveCollision(p, b) {
    if (b.x + b.radius > p.x && b.x - b.radius < p.x + p.w &&
        b.y + b.radius > p.y && b.y - b.radius < p.y + p.h) {
        
        b.dy = -8; 
        b.dx = (b.x - (p.x + p.w / 2)) * 0.5;
        // Verhindert das Eindringen in den Spieler
        if(b.y > p.y) b.y = p.y - b.radius;
    }
}

function update() {
    if (!gameActive) return;
    if (!isPaused) {
        if (keys['KeyA'] && p1.x > 0) p1.x -= 5;
        if (keys['KeyD'] && p1.x < 665) p1.x += 5;
        if (keys['KeyW'] && !p1.jump) { p1.dy = -10; p1.jump = true; }

        if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 5;
        if (keys['ArrowRight'] && p2.x < 665) p2.x += 5;
        if (keys['ArrowUp'] && !p2.jump) { p2.dy = -10; p2.jump = true; }

        [p1, p2].forEach(p => {
            p.y += p.dy;
            if (p.y < 350) p.dy += gravity;
            else { p.y = 350; p.dy = 0; p.jump = false; }
        });

        ball.x += ball.dx; ball.y += ball.dy;
        ball.dy += gravity * 0.5;
        ball.dx *= 0.99;

        // Banden-Kollision
        if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.7; }
        if (ball.x < ball.radius) { ball.x = ball.radius; ball.dx *= -0.7; }
        if (ball.x > 700 - ball.radius) { ball.x = 700 - ball.radius; ball.dx *= -0.7; }
        if (ball.y > 390) { ball.y = 390; ball.dy *= -0.5; ball.dx *= 0.9; }

        // Torpfosten/Latte
        if (ball.y > 270 && ball.y < 290) {
            if (ball.x < 40) { ball.dy = -5; ball.dx = 4; }
            if (ball.x > 660) { ball.dy = -5; ball.dx = -4; }
        }

        // Tor-Check
        if (ball.y > 285) {
            if (ball.x < 20) handleGoal(2);
            if (ball.x > 680) handleGoal(1);
        }

        [p1, p2].forEach(p => resolveCollision(p, ball));
    }

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0,0,700,400);
    
    // Hintergrund: Oben Stadion, unten Rasen
    ctx.fillStyle = "#1a1a2e"; ctx.fillRect(0, 0, 700, 250);
    ctx.fillStyle = "#2e7d32"; ctx.fillRect(0, 250, 700, 150);
    
    // Feldlinien
    ctx.strokeStyle = "rgba(255,255,255,0.2)"; ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 680, 380);
    ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();
    ctx.beginPath(); ctx.arc(350, 325, 40, 0, Math.PI*2); ctx.stroke();

    // Tore (Links und Rechts)
    ctx.strokeStyle = "#fff"; ctx.lineWidth = 6;
    ctx.strokeRect(-2, 280, 25, 120); // Links
    ctx.strokeRect(677, 280, 25, 120); // Rechts

    // Spieler
    [p1, p2].forEach(p => {
        ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.fillStyle = "#ffdbac"; ctx.fillRect(p.x + 5, p.y - 15, 25, 15);
        ctx.strokeStyle = "black"; ctx.lineWidth = 1; ctx.strokeRect(p.x, p.y, p.w, p.h);
    });

    // Ball
    ctx.fillStyle = "white"; ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = "black"; ctx.stroke();
}

function endGame() {
    gameActive = false;
    alert("SPIEL ENDE! " + score1 + " : " + score2);
    showMenu();
}
</script>
"""

components.html(game_html, height=750, scrolling=False)
