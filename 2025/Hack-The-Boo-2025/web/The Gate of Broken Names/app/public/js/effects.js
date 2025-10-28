
// Create raindrops
function createRaindrops(count = 50) {
  const container = document.getElementById('rain-container');
  if (!container) return;
  
  for (let i = 0; i < count; i++) {
    const raindrop = document.createElement('div');
    raindrop.className = 'raindrop';
    const left = Math.random() * 100;
    const delay = Math.random() * 2;
    const duration = 0.5 + Math.random() * 0.5;
    raindrop.style.left = `${left}%`;
    raindrop.style.animationDelay = `${delay}s`;
    raindrop.style.animationDuration = `${duration}s`;
    container.appendChild(raindrop);
  }
}

// Vary rain intensity
function varyRainIntensity() {
  const raindrops = document.querySelectorAll('.raindrop');
  raindrops.forEach(drop => {
    const intensity = 0.3 + Math.random() * 0.7;
    drop.style.opacity = intensity;
  });
}

// Vary fog density
function varyFogDensity() {
  const fogLayers = document.querySelectorAll('.fog-layer');
  fogLayers.forEach((layer, index) => {
    const density = 0.5 + Math.random() * 0.5;
    layer.style.opacity = density * (1 - index * 0.2);
  });
}

// Initialize effects
document.addEventListener('DOMContentLoaded', () => {
  // Create raindrops
  createRaindrops(50);
  
  // Vary rain intensity periodically
  setInterval(varyRainIntensity, 3000);
  
  // Vary fog density periodically
  setInterval(varyFogDensity, 5000);
  
});

