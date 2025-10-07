document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar no mobile
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }
    
    // Fechar sidebar ao clicar fora (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
    
    // --- LÓGICA MELHORADA PARA MARCAR ITEM ATIVO ---
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    let bestMatch = null;

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        // Ignora links vazios ou que são apenas âncoras
        if (!linkPath || linkPath === '#') {
            return;
        }

        // O link para o painel principal deve ser uma correspondência exata
        if (linkPath === '/painel' && currentPath === '/painel') {
             bestMatch = link;
             return; // Encontrou o painel, não precisa de mais nada
        }

        // Para outros links, verifica se a URL atual começa com o caminho do link
        // e não é o próprio painel (para evitar que o painel corresponda a tudo)
        if (linkPath !== '/painel' && currentPath.startsWith(linkPath)) {
            // Se ainda não houver uma melhor correspondência, ou se esta for mais específica (mais longa)
            if (!bestMatch || linkPath.length > bestMatch.getAttribute('href').length) {
                bestMatch = link;
            }
        }
    });

    // Se encontrarmos a melhor correspondência, ativa o item pai na lista
    if (bestMatch) {
        bestMatch.parentElement.classList.add('active');
    }
});