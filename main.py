@app.post("/diagnostico/processar/completo")
def processar_diagnostico_completo(dados: PayloadDiagnosticoARCA):
    score_total = int(
        dados.score_pilar_a1 +
        dados.score_pilar_r +
        dados.score_pilar_c +
        dados.score_pilar_a2
    )

    if score_total <= 40:
        classificacao = "CRÍTICA"
    elif score_total <= 75:
        classificacao = "ALTA"
    else:
        classificacao = "MÉDIA"

    relatorio_agente_ia = gerar_analise_agente_ia(
        dados,
        score_total
    )

    corpo_email_formatado = f"""
Olá, {dados.responsavel},

Segue o relatório técnico estruturado gerado pelo Agente de IA do Framework ARCA para a empresa {dados.empresa}.

----------------------------------------------------------------------
📊 DADOS CONSOLIDADOS DO LEAD
----------------------------------------------------------------------
🏢 Organização: {dados.empresa}
👤 Gestor Responsável: {dados.responsavel}
📱 Canal WhatsApp: {dados.whatsapp}

📈 SCORE ARCA CALCULADO: {score_total} de 100 pontos.
⚠️ CLASSIFICAÇÃO DE RISCO: {classificacao}

----------------------------------------------------------------------
🤖 ANÁLISE REAL DO AGENTE DE IA ARCA:
----------------------------------------------------------------------
{relatorio_agente_ia}

----------------------------------------------------------------------
🚀 PRÓXIMO PASSO RECOMENDADO:
Acesse a agenda do consultor Adriano Moreira no link abaixo para validar o plano de 90 dias focado em ganho de receita:

https://calendar.app.google/C1d44pbpqbLmU17m7

Atenciosamente,
Equipe ARCA Governance & Grupo Gestão Integrada
"""

    envio_sucesso = disparar_emails_reais(
        dados.email,
        f"Resultado Diagnóstico ARCA - {dados.empresa}",
        corpo_email_formatado.strip()
    )

    if envio_sucesso:
        status_email = (
            f"Relatório enviado com sucesso para "
            f"{dados.email} (com cópia para a diretoria)!"
        )
    else:
        status_email = "Relatório exibido na tela com sucesso."

    return {
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": relatorio_agente_ia,
        "confirmacao_envio": {
            "email_status": status_email,
            "whatsapp_status": (
                "Plano de melhorias gerado com sucesso."
            )
        }
    }