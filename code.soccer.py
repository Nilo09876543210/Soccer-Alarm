import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga 1v1 Ultimate", layout="centered")

# Wir nutzen Streamlit nur als Container, die gesamte Logik (Menü + Spiel) läuft im HTML-Teil
game_html = """
<div id="main-container" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 20px; font-family: 'Arial', sans-serif; color: white; min-height: 600px; box-shadow: 0 10px 50px rgba(0,0,0,0.8);">
    
    <!-- STARTMENÜ -->
    <div id="menu" style="text-align: center; width: 100%;">
        <h1 style="font-size: 40px; color: #f1c40f; text-shadow: 2px 2px #000;">BUNDESLIGA 1v1</h1>
        <p>Wähle deine Teams:</p>
        
        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div style="background: #222; padding: 15px; border-radius: 10px; border: 2px solid #3498db;">
                <h3>Spieler 1 (WASD)</h3>
                <select id="p1Select" style="padding: 10px; font-size: 16px;">
                    <option value="HSV" data-color="#3498db">HSV (Blau)</option>
                    <option value="Werder" data-color="#2e7d32">Werder Bremen (Grün)</option>
                    <option value="Bayern" data-color="#e74c3c">FC Bayern (Rot)</option>
                    <option value="BVB" data-color="#f1c40f">BVB (Gelb)</option>
                </select>
            </div>
            <div style="background: #222; padding: 15px; border-radius: 10px; border: 2px solid #e74c3c;">
                <h3>Spieler 2 (Pfeile)</h3>
                <select id="p2Select" style="padding: 10px; font-size: 16px;">
                    <option value="Bayern" data-color="#e74c3c">FC Bayern (Rot)</option>
                    <option value="Werder" data-color="#2e7d32">Werder Bremen (Grün)</option>
                    <option value="HSV" data-color="#3498db">HSV (Blau)</option>
                    <option value="BVB" data-color="#f1c40f">BVB (Gelb)</option>
                </select>
            </div>
        </div>
        
        <button onclick="startGame()" style="margin-top: 40px; padding: 15px 50px; font-size: 24px; background: #27ae60; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; transition: 0.3s;">ANPFIFF!</button>
    </div>

    <!-- SPIELBEREICH (versteckt bis Start) -->
    <div id="game-area" style="display: none; width: 100%; text-align: center;">
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 10px;">
            <button onclick="showMenu()" style="background: #555; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer;">Home Menü</button>
            <div style="font-size: 20px; font-weight: bold;">
                <span id="p1-name-display">P1</span> <span id="score-display">0 : 0</span> <span id="p2-name-display">P2</span>
            </div>
            <div id="timer-display" style="font-family: monospace; font-size: 18px; color: #0f0;">120s</div>
        </div>
        <canvas id="gameCanvas" width="700" height="400" style="border: 4px solid #444; border-radius: 10px; background: #1a5e1a;"></canvas>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const teams = {
    "HSV": "#3498db",
    "Werder": "#2ecc71",
    "Bayern": "#e74c3c",
    "BVB": "#f1c40f"
};

let gameActive = false;
let timeLeft = 120;
let score1 = 0;
let score2 = 0;
let timerInterval;

const gravity = 0.45;
const keys = {};

// Objekte
let ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
let p1 = { x: 70, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#3498db", name: "HSV" };
let p2 = { x: 595, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#e74c3c", name: "Bayern" };

window.addEventListener("keydown", e => {
    if(gameActive) {
        keys[e.code] = true;
        if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)) e.preventDefault();
    }
});
window.addEventListener("keyup", e => keys[e.code] = false);

function startGame() {
    const s1 = document.getElementById("p1Select");
    const s2 = document.getElementById("p2Select");
    
    p1.name = s1.value;
    p1.color = teams[s1.value];
    p2.name = s2.value;
    p2.color = teams[s2.value];
    
    document.getElementById("p1-name-display").innerText = p1.name;
    document.getElementById("p1-name-display").style.color = p1.color;
    document.getElementById("p2-name-display").innerText = p2.name;
    document.getElementById("p2-name-display").style.color = p2.color;

    document.getElementById("menu").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    
    gameActive = true;
    score1 = 0; score2 = 0; timeLeft = 120;
    resetRound();
    
    if(timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if(timeLeft > 0) {
            timeLeft--;
            document.getElementById("timer-display").innerText = timeLeft + "s";
        } else {
            endGame();
        }
    }, 1000);

    // WICHTIG: Fokus setzen damit Steuerung klappt
    window.focus();
    update();
}

function showMenu() {
    gameActive = false;
    clearInterval(timerInterval);
    document.getElementById("menu").style.display = "block";
    document.getElementById("game-area").style.display = "none";
}

function resetRound() {
    p1.x = 70; p1.y = 350; p1.dy = 0;
    p2.x = 595; p2.y = 350; p2.dy = 0;
    ball.x = 350; ball.y = 30; ball.dx = (Math.random()-0.5)*6; ball.dy = 0;
}

function checkCollision(p, b) {
    let closeX = Math.max(p.x, Math.min(b.x, p.x + p.w));
    let closeY = Math.max(p.y, Math.min(b.y, p.y + p.h));
    let dX = b.x - closeX;
    let dY = b.y - closeY;
    return (dX * dX + dY * dY) < (b.radius * b.radius);
}

function update() {
    if (!gameActive) return;

    if (keys['KeyA'] && p1.x > 0) p1.x -= 7;
    if (keys['KeyD'] && p1.x < 665) p1.x += 7;
    if (keys['KeyW'] && !p1.jump) { p1.dy = -12; p1.jump = true; }

    if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 7;
    if (keys['ArrowRight'] && p2.x < 665) p2.x += 7;
    if (keys['ArrowUp'] && !p2.jump) { p2.dy = -12; p2.jump = true; }

    [p1, p2].forEach(p => {
        p.y += p.dy;
        if (p.y < 350) p.dy += gravity;
        else { p.y = 350; p.dy = 0; p.jump = false; }
    });

    ball.x += ball.dx; ball.y += ball.dy;
    ball.dy += gravity * 0.7;
    ball.dx *= 0.993;

    if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.8; }
    if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.8; }
    if (ball.y > 390) { ball.y = 390; ball.dy *= -0.6; ball.dx *= 0.95; }

    // Latten-Check
    if (ball.y > 270 && ball.y < 295) {
        if (ball.x < 35) { ball.dy = -6; ball.dx = 5; }
        if (ball.x > 665) { ball.dy = -6; ball.dx = -5; }
    }

    if (ball.y > 280) {
        if (ball.x < 15) { score2++; resetRound(); }
        if (ball.x > 685) { score1++; resetRound(); }
    }

    [p1, p2].forEach(p => {
        if (checkCollision(p, ball)) {
            ball.dy = -10;
            ball.dx = (ball.x - (p.x + p.w/2)) * 0.9;
        }
    });

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.fillStyle = "#16213e";
    ctx.fillRect(0, 0, 700, 400);
    
    // Rasen
    ctx.fillStyle = "#2e7d32";
    ctx.fillRect(0, 250, 700, 150);
    
    // Linien
    ctx.strokeStyle = "rgba(255,255,255,0.3)";
    ctx.lineWidth = 2;
    ctx.strokeRect(5, 5, 690, 390);
    ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();

    // Tore
    ctx.strokeStyle = "white"; ctx.lineWidth = 5;
    ctx.strokeRect(-5, 280, 25, 120);
    ctx.strokeRect(680, 280, 25, 120);

    // Spieler
    [p1, p2].forEach(p => {
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.fillStyle = "#ffdbac";
        ctx.fillRect(p.x + 5, p.y - 18, 25, 18);
    });

    // Ball
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2);
    ctx.fill();

    document.getElementById("score-display").innerText = score1 + " : " + score2;
}

function endGame() {
    gameActive = false;
    alert("SPIEL ENDE! " + p1.name + " " + score1 + " : " + score2 + " " + p2.name);
    showMenu();
}
</script>
"""

components.html(game_html, height=650)
