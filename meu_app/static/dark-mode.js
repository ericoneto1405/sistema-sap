/**
 * Sistema de Modo Noturno
 * Persiste a preferência do usuário no localStorage
 */

(function() {
    'use strict';
    
    // Elementos
    const toggle = document.getElementById('dark-mode-toggle');
    const sunIcon = toggle.querySelector('.sun-icon');
    const moonIcon = toggle.querySelector('.moon-icon');
    
    // Verificar preferência salva
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Aplicar tema inicial
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        enableDarkMode(false);
    }
    
    // Event listener para o toggle
    toggle.addEventListener('click', function() {
        const isDark = document.body.classList.contains('dark-mode');
        
        if (isDark) {
            disableDarkMode();
        } else {
            enableDarkMode(true);
        }
    });
    
    /**
     * Ativa o modo escuro
     * @param {boolean} animate - Se deve animar a transição
     */
    function enableDarkMode(animate = true) {
        if (animate) {
            toggle.classList.add('rotating');
            setTimeout(() => toggle.classList.remove('rotating'), 500);
        }
        
        document.body.classList.add('dark-mode');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
        localStorage.setItem('theme', 'dark');
        
        // Dispatch evento customizado
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: 'dark' } }));
    }
    
    /**
     * Desativa o modo escuro
     */
    function disableDarkMode() {
        toggle.classList.add('rotating');
        setTimeout(() => toggle.classList.remove('rotating'), 500);
        
        document.body.classList.remove('dark-mode');
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
        localStorage.setItem('theme', 'light');
        
        // Dispatch evento customizado
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: 'light' } }));
    }
    
    // Escutar mudanças de preferência do sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        const savedTheme = localStorage.getItem('theme');
        
        // Só aplicar se não houver preferência salva
        if (!savedTheme) {
            if (e.matches) {
                enableDarkMode(false);
            } else {
                disableDarkMode();
            }
        }
    });
    
    console.log('🌙 Modo noturno inicializado');
})();

