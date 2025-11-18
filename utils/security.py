# utils/security.py
import bcrypt
import re
from email_validator import validate_email, EmailNotValidError
import bleach


def hash_password(password):
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_email_address(email):
    """Valida formato de email"""
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def validate_phone(phone):
    """Valida telefone brasileiro (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
    pattern = r'^\(\d{2}\)\s?\d{4,5}-?\d{4}$'
    return bool(re.match(pattern, phone))


def validate_cnh(cnh):
    """
    Valida CNH brasileira (Carteira Nacional de Habilitação)
    - Deve ter exatamente 11 dígitos
    - Usa algoritmo de validação com dígitos verificadores
    """
    # Remove espaços ou caracteres especiais
    cnh = re.sub(r'\D', '', str(cnh))
    
    # Verifica se tem exatamente 11 dígitos
    if len(cnh) != 11:
        return False, "CNH deve conter exatamente 11 dígitos"
    
    # Verifica se não é uma sequência de números iguais (ex: 11111111111)
    if len(set(cnh)) == 1:
        return False, "CNH inválida (sequência repetida)"
    
    # Calcula primeiro dígito verificador
    dsc = 0
    v = 9
    for i in range(9):
        dsc += int(cnh[i]) * v
        v -= 1
    
    first_digit = dsc % 11
    if first_digit >= 10:
        first_digit = 0
    
    # Calcula segundo dígito verificador
    dsc = 0
    v = 1
    for i in range(9):
        dsc += int(cnh[i]) * v
        v += 1
    
    second_digit = dsc % 11
    if second_digit >= 10:
        second_digit = 0
    
    # Valida os dígitos verificadores
    if int(cnh[9]) != first_digit or int(cnh[10]) != second_digit:
        return False, "CNH inválida (dígitos verificadores incorretos)"
    
    return True, cnh


def validate_cpf(cpf):
    """
    Valida CPF brasileiro
    - Deve ter exatamente 11 dígitos
    - Usa algoritmo de validação com dígitos verificadores
    """
    # Remove espaços ou caracteres especiais
    cpf = re.sub(r'\D', '', str(cpf))
    
    # Verifica se tem exatamente 11 dígitos
    if len(cpf) != 11:
        return False, "CPF deve conter exatamente 11 dígitos"
    
    # Verifica se não é uma sequência de números iguais (ex: 11111111111)
    if len(set(cpf)) == 1:
        return False, "CPF inválido (sequência repetida)"
    
    # Calcula primeiro dígito verificador
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = (sum_digits * 10) % 11
    if first_digit >= 10:
        first_digit = 0
    
    # Calcula segundo dígito verificador
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = (sum_digits * 10) % 11
    if second_digit >= 10:
        second_digit = 0
    
    # Valida os dígitos verificadores
    if int(cpf[9]) != first_digit or int(cpf[10]) != second_digit:
        return False, "CPF inválido (dígitos verificadores incorretos)"
    
    return True, cpf


def validate_password_strength(password):
    """
    Valida força da senha:
    - Mínimo 6 caracteres
    - Pelo menos 1 letra
    - Pelo menos 1 número
    """
    if len(password) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    if not re.search(r'[A-Za-z]', password):
        return False, "Senha deve conter pelo menos uma letra"
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"
    return True, "Senha válida"


def sanitize_input(text):
    """Remove tags HTML e scripts maliciosos"""
    if not text:
        return ""
    return bleach.clean(text, tags=[], strip=True)


def validate_text_input(text, field_name, min_length=1, max_length=200):
    """Valida texto genérico"""
    if not text or not text.strip():
        return False, f"{field_name} é obrigatório"
    
    text = sanitize_input(text)
    
    if len(text) < min_length:
        return False, f"{field_name} deve ter no mínimo {min_length} caracteres"
    if len(text) > max_length:
        return False, f"{field_name} deve ter no máximo {max_length} caracteres"
    
    return True, text


def validate_number(value, field_name, min_val=None, max_val=None):
    """Valida números"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False, f"{field_name} deve ser maior que {min_val}"
        if max_val is not None and num > max_val:
            return False, f"{field_name} deve ser menor que {max_val}"
        return True, num
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número válido"