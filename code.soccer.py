import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bundesliga 1v1 Arena", layout="centered")

st.title("⚽ Bundesliga 1v1: Nord-Süd-Gipfel")

game_html = """
<div id="wrapper" style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 25px; border-radius: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: white; box-shadow: 0 10px 60px rgba(0,0,0,0.7);">
    
    <!-- Scoreboard -->
    <div style="display: flex; align-items: center; justify-content: center; gap: 40px; margin-bottom: 10px;">
        <div style="text-align: center;">
            <div style="font-size: 24px; color: #3498db; font-weight: bold;">HSV</div>
            <div id="p1-score" style="font-size: 50px; font-weight: 900;">0</div>
        </div>
        <div style="font-size: 30px; color: #555; margin-top: 20px;">VS</div>
        <div style="text-align: center;">
            <div style="font-size: 24px; color: #e74c3c; font-weight: bold;">FC BAYERN</div>
            <div id="p2-score" style="font-size: 50px; font-weight: 900;">0</div>
        </div>
    </div>

    <!-- Timer & Status -->
    <div style="background: rgba(255,255,255,0.1); padding: 5px 20px; border-radius: 50px; margin-bottom: 20px;">
        <span style="color: #0f0;">⏱</span> <span id="timer" style="font-family: monospace; font-size: 20px;">120</span>s
    </div>
    
    <canvas id="gameCanvas" width="700" height="400" style="border: 4px solid #444; border-radius: 10px; background: #2e7d32;"></canvas>
    
    <div style="margin-top: 20px; font-size: 13px; color: #777; text-align: center;">
        <b>HSV:</b> WASD | <b>Bayern:</b> Pfeiltasten<br>
        <span style="color: #aaa;">Klicke ins Feld, um die Steuerung zu aktivieren!</span>
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const timerEl = document.getElementById("timer");
const s1El = document.getElementById("p1-score");
const s2El = document.getElementById("p2-score");

let timeLeft = 120;
let score1 = 0;
let score2 = 0;
let gameOver = false;
let flashEffect = 0;

const gravity = 0.45;
const keys = {};

// Spiel-Objekte
const ball = { x: 350, y: 50, dx: 0, dy: 0, radius: 10 };
const p1 = { startX: 70, startY: 350, x: 70, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#3498db", name: "HSV" };
const p2 = { startX: 595, startY: 350, x: 595, y: 350, w: 35, h: 50, dy: 0, jump: false, color: "#e74c3c", name: "Bayern" };

window.addEventListener("keydown", e => {
    keys[e.code] = true;
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)) e.preventDefault();
});
window.addEventListener("keyup", e => keys[e.code] = false);

function resetRound() {
    flashEffect = 15; // Kurzes Aufleuchten
    p1.x = p1.startX; p1.y = p1.startY; p1.dy = 0;
    p2.x = p2.startX; p2.y = p2.startY; p2.dy = 0;
    ball.x = 350; ball.y = 20; ball.dx = (Math.random()-0.5)*6; ball.dy = 0;
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

    // Steuerung HSV
    if (keys['KeyA'] && p1.x > 0) p1.x -= 7;
    if (keys['KeyD'] && p1.x < 665) p1.x += 7;
    if (keys['KeyW'] && !p1.jump) { p1.dy = -12; p1.jump = true; }

    // Steuerung Bayern
    if (keys['ArrowLeft'] && p2.x > 0) p2.x -= 7;
    if (keys['ArrowRight'] && p2.x < 665) p2.x += 7;
    if (keys['ArrowUp'] && !p2.jump) { p2.dy = -12; p2.jump = true; }

    // Physik Spieler
    [p1, p2].forEach(p => {
        p.y += p.dy;
        if (p.y < 350) p.dy += gravity;
        else { p.y = 350; p.dy = 0; p.jump = false; }
    });

    // Physik Ball
    ball.x += ball.dx;
    ball.y += ball.dy;
    ball.dy += gravity * 0.7;
    ball.dx *= 0.993; // Reibung

    // Kollision Decke & Wände
    if (ball.y < ball.radius) { ball.y = ball.radius; ball.dy *= -0.8; }
    if (ball.x < ball.radius || ball.x > 700 - ball.radius) { ball.dx *= -0.8; }
    if (ball.y > 390) { ball.y = 390; ball.dy *= -0.6; ball.dx *= 0.95; }

    // Latten-Check (Ball darf nicht liegen bleiben)
    if (ball.y > 270 && ball.y < 295) {
        if (ball.x < 35) { ball.dy = -6; ball.dx = 5; } // Kick von linker Latte
        if (ball.x > 665) { ball.dy = -6; ball.dx = -5; } // Kick von rechter Latte
    }

    // Tor-Abfrage
    if (ball.y > 280) {
        if (ball.x < 15) { score2++; resetRound(); }
        if (ball.x > 685) { score1++; resetRound(); }
    }

    // Spieler-Ball Kontakt
    [p1, p2].forEach(p => {
        if (checkCollision(p, ball)) {
            ball.dy = -10;
            ball.dx = (ball.x - (p.x + p.w/2)) * 0.9;
        }
    });

    if (flashEffect > 0) flashEffect--;
    draw();
    requestAnimationFrame(update);
}

function draw() {
    // 1. Hintergrund (Himmel & Tribüne)
    ctx.fillStyle = "#16213e";
    ctx.fillRect(0, 0, 700, 400);
    
    // Flutlicht-Strahlen
    ctx.fillStyle = "rgba(255,255,255,0.05)";
    ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(150,0); ctx.lineTo(350,400); ctx.fill();
    ctx.beginPath(); ctx.moveTo(700,0); ctx.lineTo(550,0); ctx.lineTo(350,400); ctx.fill();

    // Tribünen-Punkte (Fans)
    for(let i=0; i<700; i+=25) {
        for(let j=30; j<250; j+=35) {
            ctx.fillStyle = Math.random() > 0.5 ? "#333" : "#444";
            ctx.fillRect(i, j, 15, 10);
        }
    }

    // 2. Rasen
    ctx.fillStyle = "#2e7d32";
    ctx.fillRect(0, 250, 700, 150);
    
    // Spielfeld-Linien
    ctx.strokeStyle = "rgba(255,255,255,0.4)";
    ctx.lineWidth = 2;
    ctx.strokeRect(10, 250, 680, 145);
    ctx.beginPath(); ctx.moveTo(350, 250); ctx.lineTo(350, 400); ctx.stroke();
    ctx.beginPath(); ctx.arc(350, 325, 40, 0, Math.PI*2); ctx.stroke();

    // 3. Tore
    ctx.strokeStyle = "white";
    ctx.lineWidth = 5;
    ctx.strokeRect(-5, 280, 25, 120); // Tor links
    ctx.strokeRect(680, 280, 25, 120); // Tor rechts

    // 4. Spieler (mit Trikot-Details)
    [p1, p2].forEach(p => {
        // Schatten
        ctx.fillStyle = "rgba(0,0,0,0.3)";
        ctx.beginPath(); ctx.ellipse(p.x+p.w/2, 395, 20, 5, 0, 0, Math.PI*2); ctx.fill();
        
        // Körper
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.w, p.h);
        // Kopf
        ctx.fillStyle = "#ffdbac";
        ctx.fillRect(p.x + 5, p.y - 18, 25, 18);
        // Augen
        ctx.fillStyle = "black";
        ctx.fillRect(p.x + 8, p.y - 12, 4, 4);
        ctx.fillRect(p.x + 22, p.y - 12, 4, 4);
    });

    // 5. Ball (Fußball-Look)
    ctx.save();
    ctx.translate(ball.x, ball.y);
    ctx.fillStyle = "white";
    ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = "black"; ctx.lineWidth = 1; ctx.stroke();
    ctx.restore();

    // Tor-Flash-Effekt
    if (flashEffect > 0) {
        ctx.fillStyle = `rgba(255,255,255,${flashEffect/20})`;
        ctx.fillRect(0,0,700,400);
    }

    s1El.innerText = score1;
    s2El.innerText = score2;
}

const gameTimer = setInterval(() => {
    if (timeLeft > 0) {
        timeLeft--;
        timerEl.innerText = timeLeft;
    } else {
        gameOver = true;
        clearInterval(gameTimer);
        alert("SCHLUSSPFIFF! Endstand HSV " + score1 + " : " + score2 + " FC Bayern");
        location.reload();
    }
}, 1000);

update();
</script>
"""

components.html(game_html, height=650)
