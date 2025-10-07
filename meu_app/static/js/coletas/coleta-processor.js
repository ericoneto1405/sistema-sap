/**
 * Módulo ES6 para processamento de coletas
 * Encapsula a lógica de processamento de coleta com idempotência e cleanup
 */
class ColetaProcessor {
  constructor() {
    this.form = document.getElementById('formColeta');
    this.btnProcessar = document.getElementById('btnProcessar');
    this.btnLoading = document.getElementById('btnLoading');
    this._handler = null;
    this._timeoutId = null;
    this._initialized = false;
  }

  /**
   * Inicializa o processador de coleta
   * Garante idempotência para evitar múltiplas inicializações
   */
  init() {
    if (this._initialized || !this.form || !this.btnProcessar) {
      console.warn('ColetaProcessor já foi inicializado ou elementos não encontrados');
      return;
    }

    // Verificar se já foi inicializado no elemento
    if (this.form.dataset.coletaInit === '1') {
      console.warn('ColetaProcessor já foi inicializado neste formulário');
      return;
    }

    // Verificar se já foi inicializado globalmente
    if (window.__ColetaProcessorInitialized) {
      console.warn('ColetaProcessor já foi inicializado globalmente');
      return;
    }

    this.bindEvents();
    this.form.dataset.coletaInit = '1';
    window.__ColetaProcessorInitialized = true;
    this._initialized = true;
    
    console.log('ColetaProcessor inicializado com sucesso');
  }

  /**
   * Destrói o processador e limpa recursos
   */
  destroy() {
    if (this._handler && this.btnProcessar) {
      this.btnProcessar.removeEventListener('click', this._handler);
    }
    
    if (this._timeoutId) {
      clearTimeout(this._timeoutId);
      this._timeoutId = null;
    }
    
    if (this.form) {
      this.form.dataset.coletaInit = '0';
    }
    
    window.__ColetaProcessorInitialized = false;
    this._initialized = false;
    
    console.log('ColetaProcessor destruído');
  }

  /**
   * Vincula eventos ao formulário
   */
  bindEvents() {
    if (!this.btnProcessar) {
      return;
    }

    this._handler = (e) => this.handleSubmit(e);
    this.btnProcessar.addEventListener('click', this._handler);
  }

  /**
   * Manipula o envio do formulário
   * @param {Event} e - Evento de clique
   */
  async handleSubmit(e) {
    e.preventDefault();
    
    if (!this.validateForm()) {
      return;
    }

    try {
      await this.processColeta();
    } catch (error) {
      console.error('Erro ao processar coleta:', error);
      this.showError('Erro interno ao processar coleta');
    }
  }

  /**
   * Valida o formulário antes do envio
   * @returns {boolean} - True se válido, False caso contrário
   */
  validateForm() {
    const nomeRetirada = document.getElementById('nome_retirada');
    const documentoRetirada = document.getElementById('documento_retirada');
    const itensColeta = document.querySelectorAll('input[name="itens_coleta"]:checked');

    if (!nomeRetirada || !nomeRetirada.value.trim()) {
      this.showError('Nome da retirada é obrigatório');
      return false;
    }

    if (!documentoRetirada || !documentoRetirada.value.trim()) {
      this.showError('Documento da retirada é obrigatório');
      return false;
    }

    if (itensColeta.length === 0) {
      this.showError('Selecione pelo menos um item para coleta');
      return false;
    }

    // Validar quantidades
    for (const item of itensColeta) {
      const quantidadeInput = document.querySelector(`input[name="quantidade_${item.value}"]`);
      if (quantidadeInput && (!quantidadeInput.value || parseInt(quantidadeInput.value) <= 0)) {
        this.showError('Quantidade deve ser maior que zero para todos os itens');
        return false;
      }
    }

    return true;
  }

  /**
   * Processa a coleta com animação de carregamento
   */
  async processColeta() {
    this.showLoading();
    
    try {
      // Simular delay para mostrar animação
      await this.delay(2000);
      
      // Enviar formulário
      this.form.submit();
    } catch (error) {
      this.hideLoading();
      throw error;
    }
  }

  /**
   * Mostra animação de carregamento
   */
  showLoading() {
    if (this.btnProcessar) {
      this.btnProcessar.style.display = 'none';
    }
    if (this.btnLoading) {
      this.btnLoading.style.display = 'inline-block';
    }
  }

  /**
   * Esconde animação de carregamento
   */
  hideLoading() {
    if (this.btnProcessar) {
      this.btnProcessar.style.display = 'inline-block';
    }
    if (this.btnLoading) {
      this.btnLoading.style.display = 'none';
    }
  }

  /**
   * Mostra mensagem de erro
   * @param {string} message - Mensagem de erro
   */
  showError(message) {
    if (window.notificationSystem && typeof window.notificationSystem.error === 'function') {
      window.notificationSystem.error('Erro', message);
    } else {
      alert(message);
    }
  }

  /**
   * Delay para simulação
   * @param {number} ms - Milissegundos para aguardar
   * @returns {Promise} - Promise que resolve após o delay
   */
  delay(ms) {
    return new Promise(resolve => {
      this._timeoutId = setTimeout(resolve, ms);
    });
  }
}

// Inicializar automaticamente se o formulário existir
if (document.getElementById('formColeta')) {
  const processor = new ColetaProcessor();
  processor.init();
}

export default ColetaProcessor;
