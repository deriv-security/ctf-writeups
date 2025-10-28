// Atmospheric Effects - Fog, Rain, and Environmental Ambiance

class AtmosphericEffects {
    constructor() {
        this.fogLayer = document.getElementById('fog-layer');
        this.rainLayer = document.getElementById('rain-layer');
        this.init();
    }

    init() {
        this.createFog();
        this.createRain();
        this.createShadowCreatures();
        this.randomLightning();
    }

    createFog() {
        if (!this.fogLayer) return;
        
        for (let i = 0; i < 3; i++) {
            const fog = document.createElement('div');
            fog.className = 'fog';
            fog.style.animationDelay = `${i * 10}s`;
            this.fogLayer.appendChild(fog);
        }
    }

    createRain() {
        if (!this.rainLayer) return;
        
        const raindrops = 80;
        for (let i = 0; i < raindrops; i++) {
            const drop = document.createElement('div');
            drop.className = 'raindrop';
            drop.style.left = `${Math.random() * 100}%`;

            drop.style.animationDuration = `${Math.random() * 1 + 1.5}s`;
            drop.style.animationDelay = `${Math.random() * 2}s`;
            this.rainLayer.appendChild(drop);
        }
    }

    createShadowCreatures() {
        const shadowCount = 2;
        for (let i = 0; i < shadowCount; i++) {
            const shadow = document.createElement('div');
            shadow.className = 'shadow-creature';
            shadow.style.bottom = `${Math.random() * 30}%`;
            shadow.style.animationDuration = `${Math.random() * 10 + 15}s`;
            shadow.style.animationDelay = `${Math.random() * 10}s`;
            document.body.appendChild(shadow);
        }
    }

    randomLightning() {

        setInterval(() => {
            if (Math.random() > 0.90) {
                const flash = document.createElement('div');
                flash.className = 'lightning-flash';
                document.body.appendChild(flash);
                
                setTimeout(() => {
                    flash.remove();
                }, 500);
            }
        }, 1500); 
    }
}

// Initialize atmospheric effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AtmosphericEffects();
});
