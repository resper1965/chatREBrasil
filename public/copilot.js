/**
 * Chainlit Copilot Configuration
 * Este arquivo é carregado automaticamente pelo Chainlit
 * Serve como ponte para carregar nosso custom.js
 */

// Carregar custom.js dinamicamente
(function() {
    'use strict';

    console.log('🔧 Copilot.js carregado - iniciando customizações');

    // Criar e adicionar script tag para custom.js
    const script = document.createElement('script');
    script.src = '/public/custom.js';
    script.async = false; // Carregar em ordem
    script.onload = function() {
        console.log('✅ Custom.js carregado via copilot.js');
    };
    script.onerror = function() {
        console.error('❌ Erro ao carregar custom.js');
    };

    document.head.appendChild(script);

})();
