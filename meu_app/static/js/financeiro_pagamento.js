document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-pagamento');
    if (!form) {
        return;
    }

    const reciboInput = document.getElementById('recibo');
    const valorInput = document.getElementById('valor');
    const idTransacaoInput = document.querySelector('input[name="id_transacao"]');
    const ocrStatus = document.getElementById('ocr-status');
    const metodoPagamentoInput = document.getElementById('metodo_pagamento');
    const ocrUrl = form.dataset.ocrUrl;

    const parseValor = (valor) => {
        if (typeof valor === 'number') {
            return Number.isFinite(valor) ? valor : null;
        }
        if (typeof valor === 'string') {
            const sanitized = valor
                .trim()
                .replace(/\s+/g, '')
                .replace(/^R\$/i, '')
                .replace(/\.(?=\d{3}(?:\D|$))/g, '')
                .replace(',', '.');
            const parsed = Number(sanitized);
            return Number.isNaN(parsed) ? null : parsed;
        }
        return null;
    };

    if (metodoPagamentoInput) {
        metodoPagamentoInput.addEventListener('input', function () {
            if (this.value.toLowerCase().includes('pix')) {
                reciboInput.placeholder = 'Comprovante PIX (recomendado para segurança)';
                reciboInput.style.border = '2px solid #ffc107';
                reciboInput.style.backgroundColor = '#fffbf0';
            } else {
                reciboInput.placeholder = 'Recibo de Pagamento (opcional)';
                reciboInput.style.border = '';
                reciboInput.style.backgroundColor = '';
            }
        });
    }

    form.addEventListener('submit', (event) => {
        const totalPedido = parseFloat(form.dataset.total) || 0;
        const totalPago = parseFloat(form.dataset.pago) || 0;
        const novoValor = parseFloat(valorInput.value) || 0;

        if (totalPedido && (totalPago + novoValor) > totalPedido) {
            const confirmar = window.confirm(
                '⚠️ O valor inserido excede o total do pedido.\nDeseja continuar mesmo assim?'
            );
            if (!confirmar) {
                event.preventDefault();
            }
        }
    });

    if (reciboInput) {
        reciboInput.addEventListener('change', (event) => {
            const { files } = event.target;
            if (!files || !files[0]) {
                return;
            }

            if (!ocrUrl) {
                console.warn('Endpoint OCR não configurado.');
                return;
            }

            ocrStatus.innerHTML = '🔍 Processando recibo com OCR...';
            ocrStatus.style.color = '#2c3e50';
            ocrStatus.style.display = 'block';

            const formData = new FormData();
            formData.append('recibo', files[0]);
            const csrfTokenInput = form.querySelector('input[name="csrf_token"]');
            if (csrfTokenInput) {
                formData.append('csrf_token', csrfTokenInput.value);
            }

            fetch(ocrUrl, {
                method: 'POST',
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log('OCR retorno:', data);
                    let foundSomething = false;
                    ocrStatus.innerHTML = '';

                    if (data.error) {
                        ocrStatus.textContent = `❌ Erro: ${data.error}`;
                        ocrStatus.style.color = 'red';
                        return;
                    }

                    const ocrStatusText = data.ocr_status || 'unknown';
                    const ocrMessage = data.ocr_message || '';

                    const statusDiv = document.createElement('div');
                    statusDiv.style.marginBottom = '10px';
                    statusDiv.style.fontWeight = 'bold';
                    statusDiv.textContent =
                        ocrStatusText === 'success'
                            ? `🤖 ${ocrMessage}`
                            : `⚠️ ${ocrMessage}`;
                    statusDiv.style.color = ocrStatusText === 'success' ? 'green' : 'orange';
                    ocrStatus.appendChild(statusDiv);

                    if (data.valor_encontrado !== undefined && data.valor_encontrado !== null) {
                        const valorNumerico = parseValor(data.valor_encontrado);
                        if (valorNumerico !== null) {
                            valorInput.value = valorNumerico.toFixed(2);
                            foundSomething = true;
                        }
                        const valorStatus = document.createElement('div');
                        if (valorNumerico !== null) {
                            valorStatus.textContent = '✅ Valor preenchido automaticamente!';
                            valorStatus.style.color = 'green';
                        } else {
                            valorStatus.textContent =
                                '⚠️ OCR encontrou possível valor, mas não foi possível converter. Verifique manualmente.';
                            valorStatus.style.color = 'orange';
                        }
                        valorStatus.style.marginTop = '5px';
                        ocrStatus.appendChild(valorStatus);
                    }

                    if (data.id_transacao_encontrado) {
                        idTransacaoInput.value = data.id_transacao_encontrado;
                        const idStatus = document.createElement('div');
                        idStatus.innerHTML = `✅ ID da Transação: <strong>${data.id_transacao_encontrado}</strong>`;
                        idStatus.style.color = 'green';
                        idStatus.style.marginTop = '5px';
                        ocrStatus.appendChild(idStatus);
                        foundSomething = true;
                    }

                    if (data.data_encontrada) {
                        const dataStatus = document.createElement('div');
                        dataStatus.innerHTML = `📅 Data: <strong>${data.data_encontrada}</strong>`;
                        dataStatus.style.color = 'blue';
                        dataStatus.style.marginTop = '5px';
                        ocrStatus.appendChild(dataStatus);
                    }

                    if (data.banco_emitente) {
                        const bancoStatus = document.createElement('div');
                        bancoStatus.innerHTML = `🏦 Banco: <strong>${data.banco_emitente}</strong>`;
                        bancoStatus.style.color = 'blue';
                        bancoStatus.style.marginTop = '5px';
                        ocrStatus.appendChild(bancoStatus);
                    }

                    if (ocrStatusText === 'failed') {
                        const manualDiv = document.createElement('div');
                        manualDiv.textContent =
                            '💡 Digite os dados manualmente nos campos abaixo';
                        manualDiv.style.color = 'gray';
                        manualDiv.style.marginTop = '10px';
                        manualDiv.style.fontStyle = 'italic';
                        ocrStatus.appendChild(manualDiv);
                    } else if (!foundSomething && ocrStatusText === 'success') {
                        const noDataDiv = document.createElement('div');
                        noDataDiv.textContent =
                            '⚠️ Nenhum dado encontrado no recibo. Digite manualmente.';
                        noDataDiv.style.color = 'orange';
                        noDataDiv.style.marginTop = '5px';
                        ocrStatus.appendChild(noDataDiv);
                    }
                })
                .catch((error) => {
                    console.error('Erro no fetch do OCR:', error);
                    ocrStatus.innerHTML = `
                        <div style="color: orange; font-weight: bold; margin-bottom: 10px;">
                            ⚠️ OCR temporariamente indisponível
                        </div>
                        <div style="color: gray; font-style: italic; margin-top: 5px;">
                            💡 Digite os dados manualmente nos campos abaixo
                        </div>
                    `;
                });
        });
    }
});
