"""
Regras puras de domínio. Não importam nada do framework ou infraestrutura.
"""

def calcular_pontuacao_pura(dados: dict) -> int:
    # Exemplo simulado de regra de negócio pura
    score = 0
    for chave, valor in dados.items():
        if isinstance(valor, int):
            score += valor
        elif str(valor).isdigit():
            score += int(valor)
    return score

def definir_perfil(score: int) -> str:
    if score < 30:
        return "Iniciante"
    elif score < 70:
        return "Intermediário"
    return "Avançado"
