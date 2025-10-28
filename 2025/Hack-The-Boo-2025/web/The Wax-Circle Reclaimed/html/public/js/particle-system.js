// Fog System - Mystical fog layers replacing particles

class FogSystem {
    constructor() {
        this.canvas = document.getElementById('particle-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.fogLayers = [];
        this.layerCount = 4;
        
        this.resize();
        this.init();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    init() {
        // Create multiple fog layers with different properties
        for (let i = 0; i < this.layerCount; i++) {
            this.fogLayers.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                width: this.canvas.width * (1.5 + Math.random() * 0.5),
                height: this.canvas.height * (0.8 + Math.random() * 0.4),
                speedX: (Math.random() - 0.5) * 0.3,
                speedY: (Math.random() - 0.5) * 0.2,
                opacity: 0.05 + Math.random() * 0.1,
                baseOpacity: 0.05 + Math.random() * 0.1,
                pulseSpeed: 0.001 + Math.random() * 0.002,
                pulsePhase: Math.random() * Math.PI * 2,
                color: Math.random() > 0.5 ? 'purple' : 'orange',
                scale: 1 + Math.random() * 0.3
            });
        }
    }

    drawFogLayer(layer) {
        const centerX = layer.x;
        const centerY = layer.y;
        const radiusX = layer.width / 2;
        const radiusY = layer.height / 2;

        // Create radial gradient for fog
        const gradient = this.ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, radiusX
        );

        // Color based on layer type
        if (layer.color === 'purple') {
            gradient.addColorStop(0, `rgba(147, 51, 234, ${layer.opacity * 0.3})`);
            gradient.addColorStop(0.4, `rgba(147, 51, 234, ${layer.opacity * 0.2})`);
            gradient.addColorStop(0.7, `rgba(147, 51, 234, ${layer.opacity * 0.1})`);
            gradient.addColorStop(1, 'rgba(147, 51, 234, 0)');
        } else {
            gradient.addColorStop(0, `rgba(249, 115, 22, ${layer.opacity * 0.25})`);
            gradient.addColorStop(0.4, `rgba(249, 115, 22, ${layer.opacity * 0.15})`);
            gradient.addColorStop(0.7, `rgba(249, 115, 22, ${layer.opacity * 0.08})`);
            gradient.addColorStop(1, 'rgba(249, 115, 22, 0)');
        }

        // Draw elliptical fog
        this.ctx.save();
        this.ctx.translate(centerX, centerY);
        this.ctx.scale(layer.scale, layer.scale * 0.6);
        this.ctx.beginPath();
        this.ctx.arc(0, 0, radiusX, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.restore();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.fogLayers.forEach((layer) => {
            // Update position with slow drift
            layer.x += layer.speedX;
            layer.y += layer.speedY;
            
            // Wrap around screen edges
            if (layer.x < -layer.width / 2) layer.x = this.canvas.width + layer.width / 2;
            if (layer.x > this.canvas.width + layer.width / 2) layer.x = -layer.width / 2;
            if (layer.y < -layer.height / 2) layer.y = this.canvas.height + layer.height / 2;
            if (layer.y > this.canvas.height + layer.height / 2) layer.y = -layer.height / 2;
            
            // Pulse opacity for breathing effect
            layer.pulsePhase += layer.pulseSpeed;
            layer.opacity = layer.baseOpacity + Math.sin(layer.pulsePhase) * 0.03;
            
            // Subtle scale pulsing
            layer.scale = 1 + Math.sin(layer.pulsePhase * 0.5) * 0.1;
            
            // Draw the fog layer
            this.drawFogLayer(layer);
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize fog system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FogSystem();
});
