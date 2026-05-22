/**
 * Antigravity Interactive Background Canvas Animation
 * Performs a highly-optimized particle network and cursor trail effect
 * that reacts to cursor movement and color theme shifts.
 */

(function () {
    const canvas = document.createElement('canvas');
    canvas.id = 'antigravity-bg';
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext('2d');
    
    // Theme colors matching style.css design tokens
    const themeColors = {
        dark: {
            particle: 'rgba(99, 102, 241, 0.35)',      // Indigo base
            particleHover: 'rgba(129, 140, 248, 0.75)', // Light indigo active
            line: 'rgba(99, 102, 241, 0.06)',          // Semi-transparent line
            trail: 'rgba(139, 92, 246, 0.5)'            // Purple trail
        },
        light: {
            particle: 'rgba(79, 70, 229, 0.18)',       // Deep indigo base
            particleHover: 'rgba(99, 102, 241, 0.65)',  // Indigo active
            line: 'rgba(79, 70, 229, 0.04)',           // Very light connecting line
            trail: 'rgba(99, 102, 241, 0.45)'           // Soft trail
        }
    };

    let currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';

    // Monitor theme changes autonomously
    const themeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'data-theme') {
                currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            }
        });
    });
    themeObserver.observe(document.documentElement, { attributes: true });

    let particles = [];
    let trailParticles = [];
    const maxConnectionDist = 135;
    let particleCount = 75;

    // Smooth Cursor Coordinates Tracking (using easing/inertia)
    const mouse = {
        x: null,
        y: null,
        targetX: null,
        targetY: null,
        vx: 0,
        vy: 0,
        active: false,
        lastSpawnTime: 0
    };

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Responsive particle density
        particleCount = Math.min(110, Math.floor((canvas.width * canvas.height) / 16000));
        
        // Reinitialize system if count increases drastically
        while (particles.length < particleCount) {
            particles.push(new Particle());
        }
        if (particles.length > particleCount) {
            particles.splice(particleCount);
        }
    }

    class Particle {
        constructor() {
            this.reset();
            // Spread initially across screen
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
        }

        reset() {
            this.radius = Math.random() * 2.5 + 1.2; // 1.2px to 3.7px
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            // Float upwards to simulate antigravity/floating state
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = -Math.random() * 0.35 - 0.15; 
            this.alpha = Math.random() * 0.4 + 0.25;
            this.originalAlpha = this.alpha;
        }

        update(activeColors) {
            this.x += this.vx;
            this.y += this.vy;

            // Loop back from top to bottom
            if (this.y < -15) {
                this.y = canvas.height + 15;
                this.x = Math.random() * canvas.width;
                this.vy = -Math.random() * 0.35 - 0.15;
                this.vx = (Math.random() - 0.5) * 0.4;
            }
            if (this.x < -15 || this.x > canvas.width + 15) {
                this.reset();
                this.y = Math.random() * canvas.height;
            }

            // Mouse gravity attraction and interactive flow
            if (mouse.x !== null && mouse.active) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.hypot(dx, dy);

                if (dist < 180) {
                    const force = (180 - dist) / 180;
                    
                    // Pull force directed to mouse
                    this.x += (dx / dist) * force * 0.65;
                    this.y += (dy / dist) * force * 0.65;

                    // Apply cursor motion velocity inertia
                    this.vx += mouse.vx * force * 0.045;
                    this.vy += mouse.vy * force * 0.045;

                    // Enhance glow opacity
                    this.alpha = Math.min(0.9, this.originalAlpha + force * 0.35);
                } else {
                    // Decay back to neutral state
                    this.alpha += (this.originalAlpha - this.alpha) * 0.04;
                }
            } else {
                this.alpha += (this.originalAlpha - this.alpha) * 0.04;
            }

            // Damping velocity changes to prevent erratic speeding
            this.vx *= 0.96;
            this.vy *= 0.96;

            // Restoring minimum upward drift
            const targetDriftY = -0.15;
            if (this.vy > -0.1) {
                this.vy += (targetDriftY - this.vy) * 0.015;
            }
            const targetDriftX = (Math.sin(Date.now() * 0.001 + this.radius) * 0.1);
            this.vx += (targetDriftX - this.vx) * 0.01;
        }

        draw(activeColors) {
            ctx.beginPath();
            ctx.arc(this.x | 0, this.y | 0, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = activeColors.particle.replace(/[\d.]+\)$/, `${this.alpha.toFixed(2)})`);
            ctx.fill();
        }
    }

    class TrailParticle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = Math.random() * 2.2 + 0.8;
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 1.2 + 0.3;
            // Emit trail outward and slowly float up
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed - 0.4;
            this.alpha = 1.0;
            this.decay = Math.random() * 0.015 + 0.012;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.vx *= 0.97;
            this.vy *= 0.97;
            this.alpha -= this.decay;
        }

        draw(activeColors) {
            if (this.alpha <= 0) return;
            ctx.beginPath();
            ctx.arc(this.x | 0, this.y | 0, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = activeColors.trail.replace(/[\d.]+\)$/, `${this.alpha.toFixed(2)})`);
            ctx.fill();
        }
    }

    // Capture events to feed tracking
    function handleMouseMove(e) {
        mouse.targetX = e.clientX;
        mouse.targetY = e.clientY;
        mouse.active = true;

        // Spawn a trail bubble periodically during movement
        const now = Date.now();
        if (now - mouse.lastSpawnTime > 30) {
            trailParticles.push(new TrailParticle(e.clientX, e.clientY));
            mouse.lastSpawnTime = now;
        }
    }

    function handleMouseLeave() {
        mouse.active = false;
        mouse.targetX = null;
        mouse.targetY = null;
    }

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('resize', resizeCanvas);

    // Initial setups
    resizeCanvas();

    // Main animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const activeColors = themeColors[currentTheme];

        // Smoothly interpolate mouse coordinates for a trail/delay effect
        if (mouse.targetX !== null) {
            if (mouse.x === null) {
                mouse.x = mouse.targetX;
                mouse.y = mouse.targetY;
            } else {
                const prevX = mouse.x;
                const prevY = mouse.y;
                mouse.x += (mouse.targetX - mouse.x) * 0.07; // Easing coefficient
                mouse.y += (mouse.targetY - mouse.y) * 0.07;
                mouse.vx = mouse.x - prevX;
                mouse.vy = mouse.y - prevY;
            }
        } else {
            mouse.x = null;
            mouse.y = null;
            mouse.vx = 0;
            mouse.vy = 0;
        }

        // Draw connections
        ctx.beginPath();
        for (let i = 0; i < particles.length; i++) {
            const p1 = particles[i];
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.hypot(dx, dy);

                if (dist < maxConnectionDist) {
                    const ratio = (maxConnectionDist - dist) / maxConnectionDist;
                    ctx.moveTo(p1.x | 0, p1.y | 0);
                    ctx.lineTo(p2.x | 0, p2.y | 0);
                }
            }
        }
        ctx.strokeStyle = activeColors.line;
        ctx.lineWidth = 0.8;
        ctx.stroke();

        // Update and draw persistent particles
        particles.forEach(p => {
            p.update(activeColors);
            p.draw(activeColors);
        });

        // Update and draw short-lived trail particles
        for (let i = trailParticles.length - 1; i >= 0; i--) {
            const tp = trailParticles[i];
            tp.update();
            if (tp.alpha <= 0) {
                trailParticles.splice(i, 1);
            } else {
                tp.draw(activeColors);
            }
        }

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
})();
