"""
Serviço para geração de recibo de coleta em PDF
Modelo EXATO baseado na interface mostrada
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF
from datetime import datetime
import os
from flask import current_app


class ReceiptService:
    """Serviço para geração de recibos de coleta"""
    
    @staticmethod
    def gerar_recibo_pdf(coleta_data):
        """
        Gera um recibo PDF EXATO como o modelo mostrado
        
        Args:
            coleta_data: Dicionário com dados da coleta
            
        Returns:
            str: Caminho do arquivo PDF gerado
        """
        try:
            # Criar diretório de recibos se não existir
            receipts_dir = os.path.join(current_app.instance_path, 'recibos')
            os.makedirs(receipts_dir, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"recibo_coleta_{coleta_data['pedido_id']}_{timestamp}.pdf"
            filepath = os.path.join(receipts_dir, filename)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Estilo para título principal "Recibo de Coleta"
            main_title_style = ParagraphStyle(
                'MainTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para informações do pedido
            info_style = ParagraphStyle(
                'OrderInfo',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=8,
                fontName='Helvetica'
            )
            
            # Estilo para cabeçalho da tabela
            table_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para assinaturas
            signature_style = ParagraphStyle(
                'SignatureStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=15,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para documento de identificação
            doc_style = ParagraphStyle(
                'DocStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            # Lista de elementos para o PDF
            story = []
            
            # Título principal "Recibo de Coleta"
            story.append(Paragraph("📄 Recibo de Coleta", main_title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Informações do pedido e coleta
            pedido_info = f"""
            <b>Pedido:</b> #{coleta_data['pedido_id']}<br/>
            <b>Cliente:</b> {coleta_data.get('cliente_nome', 'N/A')}<br/>
            <b>Data da Coleta:</b> {coleta_data.get('data_coleta', datetime.now().strftime('%d/%m/%Y %H:%M'))}<br/>
            <b>Coletado por:</b> {coleta_data.get('nome_retirada', 'N/A')}<br/>
            <b>Liberado por:</b> {coleta_data.get('nome_conferente', 'N/A')}
            """
            story.append(Paragraph(pedido_info, info_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Cabeçalho da tabela de itens
            story.append(Paragraph("Itens Coletados", table_header_style))
            
            # Criar tabela de itens coletados
            items_data = [['Produto', 'Quantidade Coletada']]
            
            for item in coleta_data.get('itens_coleta', []):
                produto_nome = item.get('produto_nome', 'N/A')
                quantidade = item.get('quantidade', 0)
                
                items_data.append([
                    produto_nome,
                    str(quantidade)
                ])
            
            # Tabela de itens
            items_table = Table(items_data, colWidths=[12*cm, 4*cm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 1*cm))
            
            # Área de assinaturas (lado a lado)
            signature_data = [
                ['Assinatura do Cliente', 'Assinatura do Funcionário'],
                ['', ''],
                ['', ''],
                ['', ''],
                ['', ''],
                ['', ''],
                ['', '']
            ]
            
            signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('MINROWHEIGHT', (0, 1), (-1, -1), 25),
            ]))
            
            story.append(signature_table)
            story.append(Spacer(1, 0.5*cm))
            
            # Documento de identificação
            story.append(Paragraph("DOCUMENTO DE IDENTIFICAÇÃO", doc_style))
            
            # Criar retângulo tracejado para documento
            doc_drawing = Drawing(16*cm, 4*cm)
            
            # Retângulo tracejado
            rect = Rect(0, 0, 16*cm, 4*cm)
            rect.strokeColor = colors.black
            rect.strokeWidth = 2
            rect.strokeDashArray = [5, 5]
            rect.fillColor = colors.white
            doc_drawing.add(rect)
            
            story.append(doc_drawing)
            
            # Construir PDF
            doc.build(story)
            
            current_app.logger.info(f"Recibo PDF gerado: {filepath}")
            return filepath
            
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar recibo PDF: {str(e)}")
            raise e
