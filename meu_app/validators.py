"""
Módulo de Validação de Entradas
==============================

Este módulo contém funções centralizadas para validação e sanitização
de entradas do usuário, garantindo segurança contra ataques XSS e
validação de dados.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""

import re
import bleach
from datetime import datetime
from validate_docbr import CPF, CNPJ
from typing import Tuple, Optional, Any
from flask import current_app


class ValidationError(Exception):
    """Exceção personalizada para erros de validação"""
    pass


def sanitizar_texto(texto: str, max_length: int = 255) -> str:
    """
    Sanitiza texto removendo caracteres perigosos e limitando tamanho
    
    Args:
        texto: Texto a ser sanitizado
        max_length: Comprimento máximo permitido
        
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Converter para string se não for
    texto = str(texto)
    
    # Limitar comprimento
    if len(texto) > max_length:
        texto = texto[:max_length]
    
    # Remover caracteres de controle e sanitizar HTML
    texto_limpo = bleach.clean(
        texto,
        tags=[],  # Remover todas as tags HTML
        attributes={},  # Remover todos os atributos
        strip=True  # Remover tags não permitidas
    )
    
    # Remover caracteres de controle restantes
    texto_limpo = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', texto_limpo)
    
    return texto_limpo.strip()


def validar_cpf_cnpj(documento: str) -> Tuple[bool, str]:
    """
    Valida CPF ou CNPJ
    
    Args:
        documento: CPF ou CNPJ a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, tipo_documento)
    """
    if not documento:
        return False, "Documento vazio"
    
    # Limpar documento (remover pontos, traços, etc.)
    documento_limpo = re.sub(r'[^\d]', '', str(documento))
    
    if len(documento_limpo) == 11:
        cpf = CPF()
        if cpf.validate(documento_limpo):
            return True, "CPF"
        else:
            return False, "CPF inválido"
    elif len(documento_limpo) == 14:
        cnpj = CNPJ()
        if cnpj.validate(documento_limpo):
            return True, "CNPJ"
        else:
            return False, "CNPJ inválido"
    else:
        return False, "Documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos"


def validar_telefone(telefone: str) -> Tuple[bool, str]:
    """
    Valida formato de telefone brasileiro
    
    Args:
        telefone: Telefone a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, telefone_formatado)
    """
    if not telefone:
        return False, "Telefone vazio"
    
    # Limpar telefone (remover caracteres não numéricos)
    telefone_limpo = re.sub(r'[^\d]', '', str(telefone))
    
    # Validar comprimento (10 ou 11 dígitos)
    if len(telefone_limpo) == 10:
        # Telefone fixo: (XX) XXXX-XXXX
        return True, f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    elif len(telefone_limpo) == 11:
        # Celular: (XX) 9XXXX-XXXX
        if telefone_limpo[2] == '9':
            return True, f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        else:
            return False, "Celular deve começar com 9 no terceiro dígito"
    else:
        return False, "Telefone deve ter 10 ou 11 dígitos"


def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email
    
    Args:
        email: Email a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, email_limpo)
    """
    if not email:
        return False, "Email vazio"
    
    email = str(email).strip().lower()
    
    # Regex básico para validação de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, email
    else:
        return False, "Formato de email inválido"


def validar_data(data_str: str, formato: str = "%Y-%m-%d") -> Tuple[bool, Optional[datetime]]:
    """
    Valida e converte string de data
    
    Args:
        data_str: String da data
        formato: Formato esperado da data
        
    Returns:
        Tuple[bool, Optional[datetime]]: (é_válida, data_convertida)
    """
    if not data_str:
        return False, None
    
    try:
        data_convertida = datetime.strptime(str(data_str), formato)
        return True, data_convertida
    except ValueError:
        return False, None


def validar_numero(numero_str: str, tipo: str = "float", min_val: Optional[float] = None, 
                  max_val: Optional[float] = None) -> Tuple[bool, Optional[float]]:
    """
    Valida e converte string para número
    
    Args:
        numero_str: String do número
        tipo: Tipo do número ("int" ou "float")
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
        
    Returns:
        Tuple[bool, Optional[float]]: (é_válido, número_convertido)
    """
    if not numero_str:
        return False, None
    
    try:
        if tipo == "int":
            numero = int(numero_str)
        else:
            numero = float(numero_str)
        
        # Verificar limites
        if min_val is not None and numero < min_val:
            return False, None
        if max_val is not None and numero > max_val:
            return False, None
        
        return True, numero
    except (ValueError, TypeError):
        return False, None


def validar_categoria_produto(categoria: str) -> Tuple[bool, str]:
    """
    Valida categoria de produto
    
    Args:
        categoria: Categoria a ser validada
        
    Returns:
        Tuple[bool, str]: (é_válida, categoria_sanitizada)
    """
    if not categoria:
        return False, "Categoria vazia"
    
    # Lista de categorias permitidas
    categorias_validas = [
        'ALIMENTOS', 'BEBIDAS', 'LIMPEZA', 'HIGIENE', 'PAPELARIA',
        'ELETRÔNICOS', 'VESTUÁRIO', 'CASA', 'AUTOMOTIVO', 'OUTROS'
    ]
    
    categoria_upper = str(categoria).strip().upper()
    
    if categoria_upper in categorias_validas:
        return True, categoria_upper
    else:
        return False, f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}"


def validar_status_pedido(status: str) -> Tuple[bool, str]:
    """
    Valida status de pedido
    
    Args:
        status: Status a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, status_sanitizado)
    """
    if not status:
        return False, "Status vazio"
    
    # Lista de status permitidos
    status_validos = [
        'PENDENTE', 'CONFIRMADO', 'EM_PREPARACAO', 'PRONTO', 'ENTREGUE',
        'CANCELADO', 'DEVOLVIDO'
    ]
    
    status_upper = str(status).strip().upper()
    
    if status_upper in status_validos:
        return True, status_upper
    else:
        return False, f"Status deve ser um dos seguintes: {', '.join(status_validos)}"


def validar_tipo_usuario(tipo: str) -> Tuple[bool, str]:
    """
    Valida tipo de usuário
    
    Args:
        tipo: Tipo a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, tipo_sanitizado)
    """
    if not tipo:
        return False, "Tipo vazio"
    
    tipos_validos = ['admin', 'comum']
    tipo_lower = str(tipo).strip().lower()
    
    if tipo_lower in tipos_validos:
        return True, tipo_lower
    else:
        return False, f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}"


def validar_codigo_interno(codigo: str) -> Tuple[bool, str]:
    """
    Valida código interno de produto
    
    Args:
        codigo: Código a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, código_sanitizado)
    """
    if not codigo:
        return True, ""  # Código interno é opcional
    
    codigo_limpo = sanitizar_texto(codigo, 50)
    
    # Verificar se contém apenas caracteres alfanuméricos e alguns especiais
    if re.match(r'^[A-Za-z0-9_-]+$', codigo_limpo):
        return True, codigo_limpo
    else:
        return False, "Código interno deve conter apenas letras, números, hífen e underscore"


def validar_ean(ean: str) -> Tuple[bool, str]:
    """
    Valida código EAN (GTIN)
    
    Args:
        ean: Código EAN a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, EAN_sanitizado)
    """
    if not ean:
        return True, ""  # EAN é opcional
    
    # Limpar EAN (remover caracteres não numéricos)
    ean_limpo = re.sub(r'[^\d]', '', str(ean))
    
    # EAN pode ter 8, 12, 13 ou 14 dígitos
    if len(ean_limpo) in [8, 12, 13, 14]:
        return True, ean_limpo
    else:
        return False, "EAN deve ter 8, 12, 13 ou 14 dígitos"


def validar_quantidade(quantidade_str: str) -> Tuple[bool, Optional[int]]:
    """
    Valida quantidade (deve ser inteiro positivo)
    
    Args:
        quantidade_str: String da quantidade
        
    Returns:
        Tuple[bool, Optional[int]]: (é_válida, quantidade_convertida)
    """
    return validar_numero(quantidade_str, "int", min_val=0)


def validar_preco(preco_str: str) -> Tuple[bool, Optional[float]]:
    """
    Valida preço (deve ser float positivo)
    
    Args:
        preco_str: String do preço
        
    Returns:
        Tuple[bool, Optional[float]]: (é_válido, preço_convertido)
    """
    return validar_numero(preco_str, "float", min_val=0)


def validar_entrada_completa(dados: dict, regras: dict) -> Tuple[bool, dict, list]:
    """
    Valida um conjunto completo de dados baseado em regras
    
    Args:
        dados: Dicionário com os dados a serem validados
        regras: Dicionário com as regras de validação para cada campo
        
    Returns:
        Tuple[bool, dict, list]: (todos_válidos, dados_sanitizados, erros)
    """
    dados_sanitizados = {}
    erros = []
    todos_válidos = True
    
    for campo, regra in regras.items():
        valor = dados.get(campo, "")
        campo_obrigatorio = regra.get('obrigatorio', False)
        tipo_validacao = regra.get('tipo', 'texto')
        
        # Verificar se campo obrigatório está presente
        if campo_obrigatorio and not valor:
            erros.append(f"Campo '{campo}' é obrigatório")
            todos_válidos = False
            continue
        
        # Se campo não obrigatório e vazio, pular validação
        if not campo_obrigatorio and not valor:
            dados_sanitizados[campo] = ""
            continue
        
        # Aplicar validação baseada no tipo
        if tipo_validacao == 'texto':
            dados_sanitizados[campo] = sanitizar_texto(valor, regra.get('max_length', 255))
        elif tipo_validacao == 'cpf_cnpj':
            valido, resultado = validar_cpf_cnpj(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'telefone':
            valido, resultado = validar_telefone(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'email':
            valido, resultado = validar_email(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'data':
            valido, resultado = validar_data(valor, regra.get('formato', '%Y-%m-%d'))
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': Data inválida")
                todos_válidos = False
        elif tipo_validacao == 'numero':
            valido, resultado = validar_numero(
                valor, 
                regra.get('tipo_numero', 'float'),
                regra.get('min_val'),
                regra.get('max_val')
            )
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': Número inválido")
                todos_válidos = False
        elif tipo_validacao == 'categoria_produto':
            valido, resultado = validar_categoria_produto(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'status_pedido':
            valido, resultado = validar_status_pedido(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'tipo_usuario':
            valido, resultado = validar_tipo_usuario(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'codigo_interno':
            valido, resultado = validar_codigo_interno(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'ean':
            valido, resultado = validar_ean(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': {resultado}")
                todos_válidos = False
        elif tipo_validacao == 'quantidade':
            valido, resultado = validar_quantidade(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': Quantidade deve ser um número inteiro positivo")
                todos_válidos = False
        elif tipo_validacao == 'preco':
            valido, resultado = validar_preco(valor)
            if valido:
                dados_sanitizados[campo] = resultado
            else:
                erros.append(f"Campo '{campo}': Preço deve ser um número positivo")
                todos_válidos = False
    
    return todos_válidos, dados_sanitizados, erros
