    (function() {
        if (document.getElementById('antigravity-canvas')) return;
        
        const canvas = document.createElement('canvas');
        canvas.id = 'antigravity-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '-9999';
        canvas.style.pointerEvents = 'none';
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;
        
        const handleResize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', handleResize);
        
        let mouse = { x: null, y: null, radius: 180 };
        let lastMouse = { x: null, y: null };
        const trailParticles = [];
        
        const mouseMoveHandler = (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            
            if (lastMouse.x !== null && lastMouse.y !== null) {
                const distMoved = Math.sqrt(Math.pow(mouse.x - lastMouse.x, 2) + Math.pow(mouse.y - lastMouse.y, 2));
                if (distMoved > 2 && trailParticles.length < 150) {
                    for(let k = 0; k < Math.min(3, Math.floor(distMoved/3)+1); k++) {
                        trailParticles.push({
                            x: mouse.x + (Math.random() - 0.5) * 8,
                            y: mouse.y + (Math.random() - 0.5) * 8,
                            vx: (Math.random() - 0.5) * 1.2,
                            vy: (Math.random() - 0.5) * 1.2,
                            radius: Math.random() * 2.5 + 0.8,
                            alpha: 1.0,
                            decay: Math.random() * 0.02 + 0.015
                        });
                    }
                }
            }
            lastMouse.x = mouse.x;
            lastMouse.y = mouse.y;
        };
        
        const mouseLeaveHandler = () => {
            mouse.x = null;
            mouse.y = null;
        };
        
        window.addEventListener('mousemove', mouseMoveHandler);
        window.addEventListener('mouseleave', mouseLeaveHandler);
        
        const particles = [];
        const particleCount = 70;
        
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * 3.5 + 1.5,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                color: 'rgba(96, 165, 250, ' + (Math.random() * 0.35 + 0.25) + ')',
                angle: Math.random() * Math.PI * 2,
                spinSpeed: (Math.random() - 0.5) * 0.012
            });
        }
        
        let animationActive = true;
        
        function animate() {
            if (!animationActive) return;
            
            // Clean up resources if canvas is detached
            if (!document.getElementById('antigravity-canvas')) {
                animationActive = false;
                window.removeEventListener('resize', handleResize);
                window.removeEventListener('mousemove', mouseMoveHandler);
                window.removeEventListener('mouseleave', mouseLeaveHandler);
                return;
            }
            
            ctx.clearRect(0, 0, width, height);
            
            const grad = ctx.createRadialGradient(width/2, height, 0, width/2, height, Math.max(width, height));
            grad.addColorStop(0, '#1e3a8a');
            grad.addColorStop(1, '#090d16');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);
            
            for (let i = trailParticles.length - 1; i >= 0; i--) {
                const tp = trailParticles[i];
                tp.x += tp.vx;
                tp.y += tp.vy;
                tp.alpha -= tp.decay;
                
                if (tp.alpha <= 0) {
                    trailParticles.splice(i, 1);
                    continue;
                }
                
                ctx.beginPath();
                ctx.arc(tp.x, tp.y, tp.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(96, 165, 250, ${tp.alpha})`;
                ctx.fill();
            }
            
            if (mouse.x !== null && mouse.y !== null) {
                ctx.beginPath();
                ctx.arc(mouse.x, mouse.y, 6, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(96, 165, 250, 0.6)';
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(mouse.x, mouse.y, 22, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(96, 165, 250, 0.25)';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }
            
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                
                p.x += p.vx + Math.sin(p.angle) * 0.05;
                p.y += p.vy + Math.cos(p.angle) * 0.05;
                p.angle += p.spinSpeed;
                
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;
                
                if (mouse.x !== null && mouse.y !== null) {
                    const dx = p.x - mouse.x;
                    const dy = p.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouse.radius) {
                        const force = (mouse.radius - dist) / mouse.radius;
                        const angle = Math.atan2(dy, dx);
                        p.x += Math.cos(angle) * force * 1.8;
                        p.y += Math.sin(angle) * force * 1.8;
                    }
                }
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
                
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 130) {
                        ctx.beginPath();
                        ctx.strokeStyle = 'rgba(96, 165, 250, ' + (0.15 * (1 - dist / 130)) + ')';
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
                
                if (mouse.x !== null && mouse.y !== null) {
                    const dx = p.x - mouse.x;
                    const dy = p.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.strokeStyle = 'rgba(96, 165, 250, ' + (0.35 * (1 - dist / 150)) + ')';
                        ctx.lineWidth = 0.8;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.stroke();
                    }
                }
            }
            
            requestAnimationFrame(animate);
        }
        animate();
    })();