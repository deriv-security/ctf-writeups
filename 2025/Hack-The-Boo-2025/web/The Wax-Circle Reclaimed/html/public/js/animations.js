// Animation Utilities and Interactive Effects

class AnimationController {
    constructor() {
        this.init();
    }

    init() {
        this.observeElements();
        this.addHoverEffects();
        this.addClickEffects();
    }

    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.mystical-card, .feature-card, .achievement-badge').forEach(el => {
            observer.observe(el);
        });
    }

    addHoverEffects() {
        document.querySelectorAll('.feature-card').forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                card.style.animationDelay = '0s';
                card.classList.add('bounce-in');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('bounce-in');
            });
        });

        document.querySelectorAll('.achievement-badge').forEach(badge => {
            badge.addEventListener('mouseenter', () => {
                if (!badge.classList.contains('locked')) {
                    badge.classList.add('wiggle');
                }
            });
            
            badge.addEventListener('mouseleave', () => {
                badge.classList.remove('wiggle');
            });
        });
    }

    addClickEffects() {
        document.querySelectorAll('.portal-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const ripple = document.createElement('div');
                ripple.style.position = 'absolute';
                ripple.style.width = '20px';
                ripple.style.height = '20px';
                ripple.style.borderRadius = '50%';
                ripple.style.background = 'rgba(255, 255, 255, 0.5)';
                ripple.style.transform = 'translate(-50%, -50%)';
                ripple.style.animation = 'ripple-effect 0.6s ease-out';
                ripple.style.pointerEvents = 'none';
                
                const rect = button.getBoundingClientRect();
                ripple.style.left = (e.clientX - rect.left) + 'px';
                ripple.style.top = (e.clientY - rect.top) + 'px';
                
                button.style.position = 'relative';
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    createSparkle(x, y) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.left = x + 'px';
        sparkle.style.top = y + 'px';
        sparkle.style.width = '4px';
        sparkle.style.height = '4px';
        sparkle.style.background = '#f97316';
        sparkle.style.borderRadius = '50%';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '9999';
        sparkle.style.boxShadow = '0 0 10px #f97316';
        sparkle.style.animation = 'sparkle-fade 1s ease-out';
        
        document.body.appendChild(sparkle);
        setTimeout(() => sparkle.remove(), 1000);
    }
}

// Add ripple effect animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-effect {
        0% {
            width: 20px;
            height: 20px;
            opacity: 1;
        }
        100% {
            width: 200px;
            height: 200px;
            opacity: 0;
        }
    }
    
    @keyframes sparkle-fade {
        0% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        100% {
            opacity: 0;
            transform: translateY(-50px) scale(0);
        }
    }
`;
document.head.appendChild(style);

// Initialize animation controller when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AnimationController();
});
