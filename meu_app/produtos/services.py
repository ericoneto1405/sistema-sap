"""
Serviços para o módulo de produtos
Contém toda a lógica de negócio separada das rotas
"""
from ..models import db, Produto, MovimentacaoEstoque, Estoque
from flask import current_app
import pandas as pd
from io import BytesIO
from typing import Dict, Tuple, Optional, Any
import os

class ProdutoService:
    """Serviço para operações relacionadas a produtos"""
    
    @staticmethod
    def criar_produto(nome: str, categoria: str = 'OUTROS', codigo_interno: Optional[str] = None, ean: Optional[str] = None) -> Tuple[bool, str, Optional[Produto]]:
        """
        Cria um novo produto
        
        Args:
            nome: Nome do produto
            categoria: Categoria do produto (CERVEJA, NAB, OUTROS)
            codigo_interno: Código interno do produto
            ean: Código EAN do produto
            
        Returns:
            Tuple[bool, str, Optional[Produto]]: (sucesso, mensagem, produto)
        """
        try:
            # Validações
            if not nome or not nome.strip():
                return False, "Nome do produto é obrigatório", None
            
            # Verificar se já existe produto com mesmo nome
            produto_existente = Produto.query.filter_by(nome=nome.strip()).first()
            if produto_existente:
                return False, f"Já existe um produto com o nome '{nome}'", None
            
            # Verificar se já existe produto com mesmo código interno
            if codigo_interno and codigo_interno.strip():
                produto_existente = Produto.query.filter_by(codigo_interno=codigo_interno.strip()).first()
                if produto_existente:
                    return False, f"Já existe um produto com o código interno '{codigo_interno}'", None
            
            # Criar produto
            novo_produto = Produto(
                nome=nome.strip(),
                categoria=categoria.strip() if categoria else 'OUTROS',
                codigo_interno=codigo_interno.strip() if codigo_interno else None,
                ean=ean.strip() if ean else None
            )
            
            db.session.add(novo_produto)
            db.session.commit()
            
            current_app.logger.info(f"Produto criado: {novo_produto.nome} (ID: {novo_produto.id})")
            
            return True, "Produto criado com sucesso", novo_produto
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao criar produto: {str(e)}")
            return False, f"Erro ao criar produto: {str(e)}", None
    
    @staticmethod
    def atualizar_produto(produto_id: int, nome: str, categoria: str = 'OUTROS', codigo_interno: Optional[str] = None, ean: Optional[str] = None) -> Tuple[bool, str]:
        """
        Atualiza um produto existente
        
        Args:
            produto_id: ID do produto
            nome: Novo nome do produto
            categoria: Nova categoria do produto (CERVEJA, NAB, OUTROS)
            codigo_interno: Novo código interno
            ean: Novo código EAN
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto:
                return False, "Produto não encontrado"
            
            # Validações
            if not nome or not nome.strip():
                return False, "Nome do produto é obrigatório"
            
            # Verificar se já existe outro produto com mesmo nome
            produto_existente = Produto.query.filter(
                Produto.nome == nome.strip(),
                Produto.id != produto_id
            ).first()
            if produto_existente:
                return False, f"Já existe outro produto com o nome '{nome}'"
            
            # Verificar se já existe outro produto com mesmo código interno
            if codigo_interno and codigo_interno.strip():
                produto_existente = Produto.query.filter(
                    Produto.codigo_interno == codigo_interno.strip(),
                    Produto.id != produto_id
                ).first()
                if produto_existente:
                    return False, f"Já existe outro produto com o código interno '{codigo_interno}'"
            
            # Atualizar produto
            produto.nome = nome.strip()
            produto.categoria = categoria.strip() if categoria else 'OUTROS'
            produto.codigo_interno = codigo_interno.strip() if codigo_interno else None
            produto.ean = ean.strip() if ean else None
            
            db.session.commit()
            
            current_app.logger.info(f"Produto atualizado: {produto.nome} (ID: {produto.id})")
            
            return True, "Produto atualizado com sucesso"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao atualizar produto: {str(e)}")
            return False, f"Erro ao atualizar produto: {str(e)}"
    
    @staticmethod
    def excluir_produto(produto_id: int) -> Tuple[bool, str]:
        """
        Exclui um produto e todos os dados relacionados (estoque e movimentações)
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto:
                return False, "Produto não encontrado"
            
            nome_produto = produto.nome
            
            # Excluir movimentações de estoque relacionadas
            movimentacoes = MovimentacaoEstoque.query.filter_by(produto_id=produto_id).all()
            for movimentacao in movimentacoes:
                db.session.delete(movimentacao)
            
            # Excluir estoque relacionado
            estoque = Estoque.query.filter_by(produto_id=produto_id).first()
            if estoque:
                db.session.delete(estoque)
            
            # Excluir o produto
            db.session.delete(produto)
            db.session.commit()
            
            current_app.logger.info(f"Produto excluído: {nome_produto} (ID: {produto_id}) - {len(movimentacoes)} movimentações e 1 estoque removidos")
            
            return True, f"Produto excluído com sucesso! {len(movimentacoes)} movimentações de estoque também foram removidas."
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao excluir produto: {str(e)}")
            return False, f"Erro ao excluir produto: {str(e)}"
    
    @staticmethod
    def atualizar_preco_produto(produto_id: int, preco_medio: float) -> Tuple[bool, str, Optional[float]]:
        """
        Atualiza o preço médio de compra de um produto
        
        Args:
            produto_id: ID do produto
            preco_medio: Novo preço médio
            
        Returns:
            Tuple[bool, str, Optional[float]]: (sucesso, mensagem, preco_anterior)
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto:
                return False, "Produto não encontrado", None
            
            if preco_medio < 0:
                return False, "Preço médio não pode ser negativo", None
            
            preco_anterior = produto.preco_medio_compra
            produto.preco_medio_compra = preco_medio
            db.session.commit()
            
            current_app.logger.info(f"Preço atualizado para produto {produto.nome}: R$ {preco_anterior} -> R$ {preco_medio}")
            
            return True, "Preço atualizado com sucesso", preco_anterior
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao atualizar preço: {str(e)}")
            return False, f"Erro ao atualizar preço: {str(e)}", None

class ImportacaoService:
    """Serviço para operações de importação de produtos"""
    
    @staticmethod
    def importar_produtos_planilha(arquivo) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Importa produtos de uma planilha Excel
        
        Args:
            arquivo: Arquivo Excel enviado
            
        Returns:
            Tuple[bool, str, Dict]: (sucesso, mensagem, dados_detalhados)
        """
        try:
            # Validações do arquivo
            if not arquivo or arquivo.filename == '':
                return False, "Nenhum arquivo selecionado", {}
            
            if not arquivo.filename.endswith('.xlsx'):
                return False, "Arquivo deve ser .xlsx", {}
            
            # Ler o arquivo Excel
            df = pd.read_excel(arquivo)
            
            # Verificar colunas necessárias
            colunas_necessarias = ['NOME', 'CATEGORIA', 'CÓDIGO INTERNO', 'EAN']
            if not all(col in df.columns for col in colunas_necessarias):
                return False, "Colunas necessárias: NOME, CATEGORIA, CÓDIGO INTERNO, EAN", {}
            
            produtos_duplicados = []
            produtos_importados = 0
            produtos_invalidos = []
            
            for index, row in df.iterrows():
                try:
                    nome = str(row['NOME']).strip()
                    categoria = str(row['CATEGORIA']).strip() if pd.notna(row['CATEGORIA']) else 'OUTROS'
                    codigo_interno = str(row['CÓDIGO INTERNO']).strip() if pd.notna(row['CÓDIGO INTERNO']) else None
                    ean = str(row['EAN']).strip() if pd.notna(row['EAN']) else None
                    
                    # Pular linhas vazias
                    if not nome or nome == 'nan':
                        continue
                    
                    # Verificar se já existe produto
                    produto_existente = Produto.query.filter(
                        (Produto.nome == nome) | 
                        (Produto.codigo_interno == codigo_interno and codigo_interno is not None)
                    ).first()
                    
                    if produto_existente:
                        produtos_duplicados.append({
                            'nome': nome,
                            'codigo_interno': codigo_interno,
                            'linha': index + 2
                        })
                    else:
                        # Criar novo produto
                        novo_produto = Produto(
                            nome=nome,
                            categoria=categoria if categoria and categoria != 'nan' else 'OUTROS',
                            codigo_interno=codigo_interno if codigo_interno and codigo_interno != 'nan' else None,
                            ean=ean if ean and ean != 'nan' else None
                        )
                        db.session.add(novo_produto)
                        produtos_importados += 1
                        
                except Exception as e:
                    produtos_invalidos.append({
                        'linha': index + 2,
                        'erro': str(e)
                    })
                    continue
            
            db.session.commit()
            
            dados_resultado = {
                'produtos_importados': produtos_importados,
                'produtos_duplicados': produtos_duplicados,
                'produtos_invalidos': produtos_invalidos
            }
            
            current_app.logger.info(f"Importação de produtos: {produtos_importados} importados, {len(produtos_duplicados)} duplicados")
            
            return True, f"Importação concluída. {produtos_importados} produtos importados.", dados_resultado
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro na importação de produtos: {str(e)}")
            return False, f"Erro ao processar arquivo: {str(e)}", {}
    
    @staticmethod
    def importar_precos_planilha(arquivo) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Importa preços médios de produtos de uma planilha Excel
        
        Args:
            arquivo: Arquivo Excel enviado
            
        Returns:
            Tuple[bool, str, Dict]: (sucesso, mensagem, dados_detalhados)
        """
        try:
            # Validações do arquivo
            if not arquivo or arquivo.filename == '':
                return False, "Nenhum arquivo selecionado", {}
            
            if not arquivo.filename.endswith('.xlsx'):
                return False, "Arquivo deve ser .xlsx", {}
            
            # Ler o arquivo Excel
            df = pd.read_excel(arquivo)
            
            # Verificar colunas necessárias
            colunas_necessarias = ['CÓDIGO INTERNO', 'PREÇO MÉDIO']
            if not all(col in df.columns for col in colunas_necessarias):
                return False, "Colunas necessárias: CÓDIGO INTERNO, PREÇO MÉDIO", {}
            
            produtos_atualizados = 0
            produtos_nao_encontrados = []
            produtos_invalidos = []
            
            for index, row in df.iterrows():
                try:
                    codigo_interno = str(row['CÓDIGO INTERNO']).strip() if pd.notna(row['CÓDIGO INTERNO']) else None
                    preco_medio = float(row['PREÇO MÉDIO']) if pd.notna(row['PREÇO MÉDIO']) else 0.0
                    
                    if not codigo_interno:
                        continue
                    
                    produto = Produto.query.filter_by(codigo_interno=codigo_interno).first()
                    if produto:
                        produto.preco_medio_compra = preco_medio
                        produtos_atualizados += 1
                    else:
                        produtos_nao_encontrados.append({
                            'codigo_interno': codigo_interno,
                            'linha': index + 2
                        })
                        
                except Exception as e:
                    produtos_invalidos.append({
                        'linha': index + 2,
                        'erro': str(e)
                    })
                    continue
            
            db.session.commit()
            
            dados_resultado = {
                'produtos_atualizados': produtos_atualizados,
                'produtos_nao_encontrados': produtos_nao_encontrados,
                'produtos_invalidos': produtos_invalidos
            }
            
            current_app.logger.info(f"Importação de preços: {produtos_atualizados} produtos atualizados")
            
            return True, f"Preços atualizados com sucesso! {produtos_atualizados} produtos foram atualizados.", dados_resultado
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro na importação de preços: {str(e)}")
            return False, f"Erro ao processar arquivo: {str(e)}", {}

class ExportacaoService:
    """Serviço para operações de exportação de produtos"""
    
    @staticmethod
    def gerar_modelo_produtos() -> BytesIO:
        """
        Gera um arquivo Excel modelo para importação de produtos
        
        Returns:
            BytesIO: Arquivo Excel em memória
        """
        try:
            # Criar DataFrame com cabeçalhos e exemplos
            df = pd.DataFrame({
                'NOME': ['Exemplo Produto 1', 'Exemplo Produto 2', 'Exemplo Produto 3'],
                'CATEGORIA': ['CERVEJA', 'NAB', 'OUTROS'],
                'CÓDIGO INTERNO': ['COD001', 'COD002', 'COD003'],
                'EAN': ['7891234567890', '7891234567891', '7891234567892']
            })
            
            # Criar arquivo Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Produtos')
            
            output.seek(0)
            
            current_app.logger.info("Modelo de produtos gerado")
            
            return output
            
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar modelo de produtos: {str(e)}")
            raise
    
    @staticmethod
    def gerar_modelo_precos() -> BytesIO:
        """
        Gera um arquivo Excel modelo para importação de preços
        
        Returns:
            BytesIO: Arquivo Excel em memória
        """
        try:
            # Criar DataFrame com cabeçalhos e exemplos
            df = pd.DataFrame({
                'CÓDIGO INTERNO': ['COD001', 'COD002', 'COD003'],
                'PREÇO MÉDIO': [10.50, 25.75, 5.25]
            })
            
            # Criar arquivo Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Preços')
            
            output.seek(0)
            
            current_app.logger.info("Modelo de preços gerado")
            
            return output
            
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar modelo de preços: {str(e)}")
            raise


class ImportacaoServiceSeguro:
    """Serviço seguro para importação de produtos"""
    
    @staticmethod
    def importar_produtos_planilha_seguro(file_path: str) -> Tuple[bool, str, Dict]:
        """
        Importa produtos de uma planilha de forma segura e otimizada
        
        Args:
            file_path: Caminho para o arquivo seguro
            
        Returns:
            Tuple[bool, str, Dict]: (sucesso, mensagem, dados)
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                return False, "Arquivo não encontrado", {}
            
            # Ler arquivo Excel
            df = pd.read_excel(file_path)
            
            # Validar colunas obrigatórias
            colunas_obrigatorias = ['NOME', 'CATEGORIA']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltando:
                return False, f"Colunas obrigatórias faltando: {', '.join(colunas_faltando)}", {}
            
            # OTIMIZAÇÃO: Carregar todos os produtos existentes em memória
            # Isso elimina N+1 queries durante a verificação de duplicatas
            produtos_existentes = set()
            codigos_existentes = set()
            eans_existentes = set()
            
            for produto in Produto.query.all():
                produtos_existentes.add(produto.nome.lower().strip())
                if produto.codigo_interno:
                    codigos_existentes.add(produto.codigo_interno.strip())
                if produto.ean:
                    eans_existentes.add(produto.ean.strip())
            
            # Processar produtos
            produtos_criados = 0
            produtos_duplicados = []
            erros = []
            produtos_para_criar = []
            
            for index, row in df.iterrows():
                try:
                    nome = str(row['NOME']).strip()
                    categoria = str(row['CATEGORIA']).strip().upper()
                    codigo_interno = str(row.get('CÓDIGO INTERNO', '')).strip() if pd.notna(row.get('CÓDIGO INTERNO')) else None
                    ean = str(row.get('EAN', '')).strip() if pd.notna(row.get('EAN')) else None
                    
                    # Validar dados básicos
                    if not nome:
                        erros.append(f"Linha {index + 2}: Nome do produto é obrigatório")
                        continue
                    
                    # Verificar duplicatas usando sets em memória (muito mais rápido)
                    nome_lower = nome.lower().strip()
                    if nome_lower in produtos_existentes:
                        produtos_duplicados.append({
                            'linha': index + 2,
                            'nome': nome,
                            'motivo': 'Produto já existe'
                        })
                        continue
                    
                    # Verificar código interno duplicado
                    if codigo_interno and codigo_interno in codigos_existentes:
                        produtos_duplicados.append({
                            'linha': index + 2,
                            'nome': nome,
                            'motivo': 'Código interno já existe'
                        })
                        continue
                    
                    # Verificar EAN duplicado
                    if ean and ean in eans_existentes:
                        produtos_duplicados.append({
                            'linha': index + 2,
                            'nome': nome,
                            'motivo': 'EAN já existe'
                        })
                        continue
                    
                    # Adicionar à lista de produtos para criar
                    produtos_para_criar.append({
                        'nome': nome,
                        'categoria': categoria,
                        'codigo_interno': codigo_interno,
                        'ean': ean
                    })
                    
                    # Atualizar sets para evitar duplicatas dentro da mesma importação
                    produtos_existentes.add(nome_lower)
                    if codigo_interno:
                        codigos_existentes.add(codigo_interno)
                    if ean:
                        eans_existentes.add(ean)
                    
                except Exception as e:
                    erros.append(f"Linha {index + 2}: Erro ao processar - {str(e)}")
                    continue
            
            # OTIMIZAÇÃO: Criar todos os produtos de uma vez usando bulk_insert_mappings
            if produtos_para_criar:
                try:
                    # Usar bulk_insert_mappings para inserção em lote (muito mais rápido)
                    db.session.bulk_insert_mappings(Produto, produtos_para_criar)
                    db.session.commit()
                    produtos_criados = len(produtos_para_criar)
                    
                    current_app.logger.info(f"Importação em lote concluída: {produtos_criados} produtos criados")
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Erro no bulk insert: {str(e)}")
                    # Fallback: criar produtos um por um
                    produtos_criados = 0
                    for produto_data in produtos_para_criar:
                        try:
                            novo_produto = Produto(**produto_data)
                            db.session.add(novo_produto)
                            db.session.commit()
                            produtos_criados += 1
                        except Exception as e2:
                            db.session.rollback()
                            erros.append(f"Erro ao criar produto {produto_data['nome']}: {str(e2)}")
            
            # Limpar arquivo temporário
            try:
                os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f"Erro ao remover arquivo temporário: {str(e)}")
            
            # Preparar resultado
            dados = {
                'produtos_criados': produtos_criados,
                'produtos_duplicados': produtos_duplicados,
                'erros': erros
            }
            
            if produtos_criados > 0:
                mensagem = f"Importação concluída: {produtos_criados} produto(s) criado(s)"
                if produtos_duplicados:
                    mensagem += f", {len(produtos_duplicados)} duplicado(s) ignorado(s)"
                if erros:
                    mensagem += f", {len(erros)} erro(s) encontrado(s)"
                
                return True, mensagem, dados
            else:
                return False, "Nenhum produto foi criado. Verifique os dados da planilha.", dados
                
        except Exception as e:
            current_app.logger.error(f"Erro na importação segura: {str(e)}")
            
            # Limpar arquivo temporário em caso de erro
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            
            return False, f"Erro na importação: {str(e)}", {}
