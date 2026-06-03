(function() {
    if (document.getElementById('antigravity-canvas')) return;

    const canvas = document.createElement('canvas');
    canvas.id = 'antigravity-canvas';
    Object.assign(canvas.style, {
        position: 'fixed', top: '0', left: '0',
        width: '100vw', height: '100vh',
        zIndex: '-9999', pointerEvents: 'none'
    });
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let W = canvas.width = window.innerWidth;
    let H = canvas.height = window.innerHeight;

    const handleResize = () => { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; };
    window.addEventListener('resize', handleResize);

    // ── Mouse tracking ──────────────────────────────────────────
    let mouse = { x: W / 2, y: H / 2, active: false };
    const onMove = e => { mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true; };
    const onLeave = () => { mouse.active = false; };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseleave', onLeave);

    // ── Star colours ────────────────────────────────────────────
    const STAR_COLORS = [
        '#ffffff', '#d0e8ff', '#a8d4ff',   // white / ice blue
        '#b8a4ff', '#8be0ff',               // lavender / cyan
        '#ffd6a0', '#ffe5b4',               // warm gold
    ];

    // ── Stars ───────────────────────────────────────────────────
    const STAR_COUNT = 160;
    const stars = Array.from({ length: STAR_COUNT }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        ox: 0, oy: 0,          // original position (set below)
        baseR: Math.random() * 1.8 + 0.4,
        r: 0,
        vx: (Math.random() - 0.5) * 0.12,
        vy: (Math.random() - 0.5) * 0.12,
        color: STAR_COLORS[Math.floor(Math.random() * STAR_COLORS.length)],
        twinkleSpeed: Math.random() * 0.03 + 0.01,
        twinklePhase: Math.random() * Math.PI * 2,
        alpha: Math.random() * 0.5 + 0.5,
        pulseR: 0,
    }));
    stars.forEach(s => { s.ox = s.x; s.oy = s.y; s.r = s.baseR; });

    // Precompute which star pairs form "constellation" edges
    const EDGE_DIST = 140;
    const edges = [];
    for (let i = 0; i < stars.length; i++) {
        for (let j = i + 1; j < stars.length; j++) {
            const dx = stars[i].ox - stars[j].ox;
            const dy = stars[i].oy - stars[j].oy;
            if (Math.sqrt(dx*dx + dy*dy) < EDGE_DIST) edges.push([i, j]);
        }
    }

    // ── Shooting stars ──────────────────────────────────────────
    const shooters = [];
    function spawnShooter() {
        const angle = (Math.random() * 40 - 20 + 200) * Math.PI / 180; // roughly bottom-right
        const speed = Math.random() * 8 + 5;
        shooters.push({
            x: Math.random() * W * 1.3 - W * 0.15,
            y: Math.random() * H * 0.5,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            len: Math.random() * 120 + 60,
            alpha: 1,
            decay: Math.random() * 0.012 + 0.01,
            color: STAR_COLORS[Math.floor(Math.random() * 3)],
        });
    }
    setInterval(spawnShooter, 3200);

    // ── Cursor ripple ring ───────────────────────────────────────
    const ripples = [];
    let rippleCooldown = 0;

    // ── Nebula blobs (static, drawn first for atmosphere) ───────
    const nebulae = Array.from({ length: 5 }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 300 + 150,
        h: Math.floor(Math.random() * 360),
    }));

    let t = 0;
    let animActive = true;

    function draw() {
        if (!animActive) return;
        if (!document.getElementById('antigravity-canvas')) {
            animActive = false;
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseleave', onLeave);
            return;
        }

        t += 0.016;
        ctx.clearRect(0, 0, W, H);

        // ── Deep space background ─────────────────────────────
        const bg = ctx.createLinearGradient(0, 0, W * 0.4, H);
        bg.addColorStop(0, '#04060f');
        bg.addColorStop(0.5, '#060d1a');
        bg.addColorStop(1, '#080514');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, W, H);

        // ── Nebula atmosphere ─────────────────────────────────
        nebulae.forEach(n => {
            const pulse = Math.sin(t * 0.18 + n.h) * 0.018 + 0.025;
            const gr = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
            gr.addColorStop(0, `hsla(${n.h}, 80%, 60%, ${pulse})`);
            gr.addColorStop(1, 'transparent');
            ctx.fillStyle = gr;
            ctx.fillRect(0, 0, W, H);
        });

        // ── Cursor attraction field ───────────────────────────
        if (mouse.active) {
            const gr = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 220);
            gr.addColorStop(0, 'rgba(120, 100, 255, 0.12)');
            gr.addColorStop(1, 'transparent');
            ctx.fillStyle = gr;
            ctx.fillRect(0, 0, W, H);
        }

        // ── Constellation edges ───────────────────────────────
        edges.forEach(([i, j]) => {
            const a = stars[i], b = stars[j];
            const dx = a.x - b.x, dy = a.y - b.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > EDGE_DIST * 1.5) return; // skip if stars drifted apart
            const alpha = 0.18 * (1 - dist / (EDGE_DIST * 1.5)) * Math.min(a.alpha, b.alpha);
            ctx.beginPath();
            ctx.strokeStyle = `rgba(160, 190, 255, ${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
        });

        // ── Cursor-to-star lines ──────────────────────────────
        if (mouse.active) {
            stars.forEach(s => {
                const dx = s.x - mouse.x, dy = s.y - mouse.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 180) {
                    const alpha = 0.5 * (1 - dist / 180) * s.alpha;
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(180, 160, 255, ${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(s.x, s.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            });
        }

        // ── Stars ─────────────────────────────────────────────
        stars.forEach(s => {
            // Gravity: pull towards cursor
            if (mouse.active) {
                const dx = mouse.x - s.x, dy = mouse.y - s.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 200 && dist > 1) {
                    const force = (200 - dist) / 200 * 0.04;
                    s.vx += (dx / dist) * force;
                    s.vy += (dy / dist) * force;
                }
            }
            // Spring back towards original position
            s.vx += (s.ox - s.x) * 0.003;
            s.vy += (s.oy - s.y) * 0.003;

            // Damping
            s.vx *= 0.95;
            s.vy *= 0.95;

            s.x += s.vx;
            s.y += s.vy;

            // Wrap
            if (s.x < -10) s.x = W + 10;
            if (s.x > W + 10) s.x = -10;
            if (s.y < -10) s.y = H + 10;
            if (s.y > H + 10) s.y = -10;

            // Twinkle
            s.twinklePhase += s.twinkleSpeed;
            const twinkle = Math.sin(s.twinklePhase) * 0.3 + 0.7;
            s.alpha = twinkle;
            s.r = s.baseR * (0.85 + twinkle * 0.3);

            // Draw star glow
            const glow = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
            glow.addColorStop(0, s.color.replace(')', `, ${s.alpha * 0.5})`).replace('rgb', 'rgba').replace('#', 'rgba(').replace('rgba(', `${hexToRgba(s.color, s.alpha * 0.35)}`).replace('rgba(rgba(', ''));

            // Simple draw: core + soft glow
            // Core
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = s.color.startsWith('#') ? hexToRgba(s.color, s.alpha) : s.color;
            ctx.fill();

            // Cross sparkle for larger stars
            if (s.baseR > 1.4) {
                const arm = s.r * 3.5 * twinkle;
                const ga = s.alpha * 0.6;
                ctx.save();
                ctx.strokeStyle = s.color.startsWith('#') ? hexToRgba(s.color, ga) : s.color;
                ctx.lineWidth = 0.7;
                ctx.beginPath();
                ctx.moveTo(s.x - arm, s.y); ctx.lineTo(s.x + arm, s.y);
                ctx.moveTo(s.x, s.y - arm); ctx.lineTo(s.x, s.y + arm);
                ctx.stroke();
                ctx.restore();
            }

            // Outer glow halo
            const halo = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 6);
            halo.addColorStop(0, s.color.startsWith('#') ? hexToRgba(s.color, s.alpha * 0.25) : 'rgba(180,200,255,0.2)');
            halo.addColorStop(1, 'transparent');
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 6, 0, Math.PI * 2);
            ctx.fillStyle = halo;
            ctx.fill();
        });

        // ── Cursor glowing orb ────────────────────────────────
        if (mouse.active) {
            // Pulse ring
            const pulse = Math.sin(t * 3.5) * 5 + 18;
            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, pulse, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(160, 130, 255, ${0.25 + Math.sin(t * 3.5) * 0.1})`;
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Core dot
            const cg = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 10);
            cg.addColorStop(0, 'rgba(200, 180, 255, 0.9)');
            cg.addColorStop(1, 'rgba(100, 80, 220, 0)');
            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, 10, 0, Math.PI * 2);
            ctx.fillStyle = cg;
            ctx.fill();

            // Ripple spawn
            rippleCooldown--;
            if (rippleCooldown <= 0) {
                ripples.push({ x: mouse.x, y: mouse.y, r: 4, alpha: 0.5 });
                rippleCooldown = 28;
            }
        }

        // ── Ripples ───────────────────────────────────────────
        for (let i = ripples.length - 1; i >= 0; i--) {
            const rp = ripples[i];
            rp.r += 2.2;
            rp.alpha -= 0.013;
            if (rp.alpha <= 0) { ripples.splice(i, 1); continue; }
            ctx.beginPath();
            ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(160, 130, 255, ${rp.alpha})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // ── Shooting stars ────────────────────────────────────
        for (let i = shooters.length - 1; i >= 0; i--) {
            const s = shooters[i];
            s.x += s.vx; s.y += s.vy;
            s.alpha -= s.decay;
            if (s.alpha <= 0 || s.x > W + 100 || s.y > H + 100) {
                shooters.splice(i, 1); continue;
            }
            const tailX = s.x - s.vx * (s.len / Math.sqrt(s.vx*s.vx + s.vy*s.vy));
            const tailY = s.y - s.vy * (s.len / Math.sqrt(s.vx*s.vx + s.vy*s.vy));
            const sg = ctx.createLinearGradient(tailX, tailY, s.x, s.y);
            sg.addColorStop(0, `rgba(255,255,255,0)`);
            sg.addColorStop(1, s.color.startsWith('#') ? hexToRgba(s.color, s.alpha) : `rgba(255,255,255,${s.alpha})`);
            ctx.beginPath();
            ctx.moveTo(tailX, tailY);
            ctx.lineTo(s.x, s.y);
            ctx.strokeStyle = sg;
            ctx.lineWidth = 1.8;
            ctx.stroke();
        }

        requestAnimationFrame(draw);
    }

    // ── Hex colour helper ─────────────────────────────────────
    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1,3), 16);
        const g = parseInt(hex.slice(3,5), 16);
        const b = parseInt(hex.slice(5,7), 16);
        return `rgba(${r},${g},${b},${alpha.toFixed(3)})`;
    }

    draw();
})();