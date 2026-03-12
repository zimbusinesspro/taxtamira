/* Chatbot CTA - Canvas Dot Matrix Effect */
(function() {
    const canvas = document.getElementById('canvas-dot-matrix');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = canvas.closest('.chatbot-cta-container');
    
    let width, height;
    let dots = [];
    const dotSize = 2;
    const spacing = 20;

    function resize() {
        width = canvas.width = container.offsetWidth;
        height = canvas.height = container.offsetHeight;
        initDots();
    }

    function initDots() {
        dots = [];
        for (let x = spacing / 2; x < width; x += spacing) {
            for (let y = spacing / 2; y < height; y += spacing) {
                dots.push({
                    x: x,
                    y: y,
                    opacity: Math.random() * 0.1,
                    targetOpacity: Math.random() * 0.5,
                    color: [255, 255, 255] // White dots for dark green background
                });
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        dots.forEach(dot => {
            // Smoothly transition opacity
            if (Math.abs(dot.opacity - dot.targetOpacity) < 0.01) {
                dot.targetOpacity = Math.random() < 0.1 ? Math.random() * 0.8 : Math.random() * 0.2;
            }
            
            dot.opacity += (dot.targetOpacity - dot.opacity) * 0.05;
            
            ctx.fillStyle = `rgba(${dot.color[0]}, ${dot.color[1]}, ${dot.color[2]}, ${dot.opacity})`;
            ctx.beginPath();
            ctx.arc(dot.x, dot.y, dotSize, 0, Math.PI * 2);
            ctx.fill();
        });

        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    resize();
    animate();
})();
