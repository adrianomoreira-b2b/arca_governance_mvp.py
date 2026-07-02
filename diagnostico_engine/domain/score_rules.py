"""
Regras puras de domínio.
"""

CAMPOS_PONTUACAO = {
    "atracao_site",
    "marketing",
    "crm",
    "followup",
    "processo",
    "indicadores",
}


def calcular_pontuacao_pura(dados: dict) -> int:
    score = 0

    for campo in CAMPOS_PONTUACAO:
        valor = dados.get(campo, 0)

        try:
            score += int(valor)
        except (TypeError, ValueError):
            pass

    return score


def definir_perfil(score: int) -> str:
    if score < 30:
        return "Iniciante"
    elif score < 70:
        return "Intermediário"
    return "Avançado"