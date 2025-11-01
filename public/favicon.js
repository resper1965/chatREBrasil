// Custom favicon injection for Chainlit
// ness. branding support
(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNessBranding);
    } else {
        initNessBranding();
    }
    
    function initNessBranding() {
        injectFavicon();
        injectThemeLogos();
    }
    
    function injectFavicon() {
        // Remove existing favicon
        const existingLink = document.querySelector("link[rel*='icon']");
        if (existingLink) {
            existingLink.remove();
        }
        
        // Create new favicon link
        const link = document.createElement('link');
        link.rel = 'icon';
        link.type = 'image/png';
        link.href = '/public/favicon.png';
        
        // Add to head
        document.head.appendChild(link);
        
        // Also add apple-touch-icon for mobile
        const appleLink = document.createElement('link');
        appleLink.rel = 'apple-touch-icon';
        appleLink.href = '/public/icon.png';
        document.head.appendChild(appleLink);
        
        console.log('✅ ness. favicon loaded');
    }
    
    function injectThemeLogos() {
        // Detect theme change and swap logo dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    updateLogosForTheme();
                }
            });
        });
        
        // Observe body for theme changes
        if (document.body) {
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['class']
            });
        }
        
        // Initial logo setup
        updateLogosForTheme();
    }
    
    function updateLogosForTheme() {
        // Check if dark mode is active
        const isDark = document.body.classList.contains('dark') || 
                      document.documentElement.classList.contains('dark') ||
                      window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Find all logo images
        const logos = document.querySelectorAll('img[src*="logo"]');
        logos.forEach(logo => {
            if (isDark) {
                logo.src = logo.src.replace('logo-light', 'logo-dark');
            } else {
                logo.src = logo.src.replace('logo-dark', 'logo-light');
            }
        });
        
        console.log(`✅ ness. logos updated (${isDark ? 'dark' : 'light'} mode)`);
    }
})();

