/**
 * Custom JavaScript para Gabi. by ness.
 * Remove logos do Chainlit sem afetar funcionalidade MCP
 */

// Aguardar carregamento do DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Gabi. - Custom JS loaded');

    // Função para remover logo do Chainlit da tela de login
    function removeChailitLoginLogo() {
        // Seletores específicos para o logo de login
        const selectors = [
            'img[alt*="Chainlit"]',
            'img[alt*="chainlit"]',
            'form img[src*="logo"]',
            '.MuiBox-root > img:first-child',
            'div[class*="auth"] img:first-child',
            'div[class*="login"] img:first-child'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(img => {
                // Verificar se não é um ícone MCP ou funcional
                const src = img.src || '';
                const alt = img.alt || '';

                if (src.includes('chainlit') ||
                    alt.includes('Chainlit') ||
                    alt.includes('chainlit') ||
                    (!alt && src.includes('logo'))) {

                    console.log('🗑️ Removendo logo Chainlit:', src, alt);
                    img.style.display = 'none';
                    img.style.visibility = 'hidden';
                    img.style.height = '0';
                    img.style.width = '0';
                    img.style.position = 'absolute';
                    img.style.left = '-9999px';
                }
            });
        });
    }

    // Executar imediatamente
    removeChailitLoginLogo();

    // Observar mudanças no DOM (para quando o login é recarregado)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                removeChailitLoginLogo();
            }
        });
    });

    // Observar o body inteiro
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('✅ Gabi. - Logo removal active');
});

// Garantir que MCP UI permaneça visível
document.addEventListener('DOMContentLoaded', function() {
    // Não esconder elementos MCP
    const mcpObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Verificar se é um elemento MCP
                    if (node.dataset && node.dataset.mcp) {
                        console.log('✅ MCP element detected, keeping visible:', node);
                        node.style.display = '';
                        node.style.visibility = 'visible';
                    }

                    // Verificar children
                    const mcpElements = node.querySelectorAll('[data-mcp]');
                    mcpElements.forEach(el => {
                        console.log('✅ MCP child element detected, keeping visible:', el);
                        el.style.display = '';
                        el.style.visibility = 'visible';
                    });
                }
            });
        });
    });

    mcpObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
});

console.log('🚀 Gabi. by ness. - Custom branding loaded');
