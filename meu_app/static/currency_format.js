// Utilitários de formatação monetária brasileira
class CurrencyFormatter {
    /**
     * Formata um valor numérico para o padrão monetário brasileiro
     * @param {number} value - Valor a ser formatado
     * @param {boolean} showSymbol - Se deve mostrar o símbolo R$
     * @returns {string} Valor formatado (ex: R$ 10.000,00)
     */
    static formatBRL(value, showSymbol = true) {
        if (value === null || value === undefined || isNaN(value)) {
            return showSymbol ? 'R$ 0,00' : '0,00';
        }

        const formattedValue = Number(value).toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        return showSymbol ? `R$ ${formattedValue}` : formattedValue;
    }

    /**
     * Remove a formatação brasileira e retorna um número
     * @param {string} formattedValue - Valor formatado (ex: R$ 10.000,00)
     * @returns {number} Valor numérico
     */
    static parseBRL(formattedValue) {
        if (!formattedValue) return 0;
        
        // Remove R$, espaços e converte vírgula para ponto
        const cleanValue = formattedValue
            .replace(/R\$\s?/g, '')
            .replace(/\./g, '')  // Remove pontos (milhares)
            .replace(/,/g, '.'); // Substitui vírgula por ponto (decimais)
        
        return parseFloat(cleanValue) || 0;
    }

    /**
     * Formata um input em tempo real enquanto o usuário digita (VERSÃO CORRIGIDA).
     * @param {HTMLInputElement} input - O campo de input.
     */
    static formatInput(input) {
        // Pega a posição atual do cursor para restaurá-la depois
        let originalCursorPosition = input.selectionStart;
        const originalLength = input.value.length;

        // 1. Limpa o valor, mantendo apenas os dígitos
        let rawValue = input.value.replace(/\D/g, '');
        
        // Se estiver vazio, limpa o campo e sai
        if (rawValue === '' || rawValue === null) {
            input.value = '';
            return;
        }

        // 2. Converte a string de dígitos em um número (tratando como centavos)
        // Ex: '12345' se torna 123.45
        const numericValue = parseInt(rawValue, 10) / 100;

        // 3. Formata o número para o padrão BRL
        const formattedValue = this.formatBRL(numericValue);
        
        // 4. Atualiza o valor do input
        input.value = formattedValue;
        
        // 5. Restaura a posição do cursor de forma inteligente
        const newLength = input.value.length;
        // Calcula a nova posição do cursor com base na diferença de tamanho (ex: adição de um '.')
        const newCursorPosition = originalCursorPosition + (newLength - originalLength);
        
        // Garante que a posição não seja inválida
        if (newCursorPosition > 0 && newCursorPosition <= newLength) {
             input.setSelectionRange(newCursorPosition, newCursorPosition);
        }
    }

    /**
     * Aplica formatação automática em todos os campos de moeda
     */
    static initializeInputs() {
        const currencyInputs = document.querySelectorAll('.currency-input, input[data-currency="true"]');
        
        currencyInputs.forEach(input => {
            if (input.dataset.currencyInitialized === 'true') {
                return;
            }
            input.dataset.currencyInitialized = 'true';

            // Formata o valor inicial, se houver
            if (input.value) {
                const numericValue = this.parseBRL(input.value);
                input.value = this.formatBRL(numericValue);
            }

            // Adiciona o evento de digitação
            input.addEventListener('input', () => {
                this.formatInput(input);
            });

            // Opcional: Formatar ao perder o foco para garantir
            input.addEventListener('blur', () => {
                 if (input.value) {
                    const numericValue = this.parseBRL(input.value);
                    input.value = this.formatBRL(numericValue);
                 }
            });
        });
    }

    /**
     * Atualiza todos os elementos com classe .currency-value
     */
    static updateDisplayValues() {
        const currencyElements = document.querySelectorAll('.currency-value');
        
        currencyElements.forEach(element => {
            const value = parseFloat(element.dataset.value);
            if (!isNaN(value)) {
                element.textContent = this.formatBRL(value);
            }
        });
    }
}

// Função global para compatibilidade
window.formatCurrencyBRL = function(value, showSymbol = true) {
    return CurrencyFormatter.formatBRL(value, showSymbol);
};

window.parseCurrencyBRL = function(formattedValue) {
    return CurrencyFormatter.parseBRL(formattedValue);
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    CurrencyFormatter.initializeInputs();
    CurrencyFormatter.updateDisplayValues();
});

// Função para substituir toFixed(2) por formatação brasileira
Number.prototype.toBRL = function(showSymbol = true) {
    return CurrencyFormatter.formatBRL(this, showSymbol);
};

// Função de substituição para usar em templates
window.replaceCurrencyFormat = function() {
    // Substituir todos os elementos que usam toFixed(2)
    const elements = document.querySelectorAll('[data-currency-auto]');
    elements.forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        if (!isNaN(value)) {
            element.textContent = CurrencyFormatter.formatBRL(value);
        }
    });
};