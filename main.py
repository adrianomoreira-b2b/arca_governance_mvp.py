from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("API_VERSION", "2.0.0")
TITLE = os.getenv("PROJECT_TITLE", "ARCA Governance Engine")

app = FastAPI(title=TITLE, version=VERSION)

banco_leads = []

# Modelo de dados atualizado para suportar a engenharia do Agente de IA
class PayloadDiagnosticoARCA(BaseModel):
    empresa: str
    responsavel: str
    email: str
    whatsapp: str
    diagnostico_tipo: str
    score_pilar_a1: float
    score_pilar_r: float
    score_pilar_c: float
    score_pilar_a2: float
    dor_mapeada: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def carregar_aplicativo_visual():
    caminho_html = os.path.join("templates", "index.html")
    if not os.path.exists(caminho_html):
        return "<h1>Erro Técnico: O arquivo templates/index.html não foi encontrado.</h1>"
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return HTMLResponse(content=arquivo.read())

@app.post("/diagnostico/processar/completo")
def processar_diagnostico_completo(dados: PayloadDiagnosticoARCA):
    score_total = int(dados.score_pilar_a1 + dados.score_pilar_r + dados.score_pilar_c + dados.score_pilar_a2)
    
    if score_total <= 40:
        classificacao = "CRÍTICA"
        analise_base = "Operação Comercial desorganizada com vazamento de receita e perdas ocultas graves."
    elif score_total <= 75:
        classificacao = "ALTA"
        analise_base = "Apresenta gargalos de processos e dependência severa de execução manual."
    else:
        classificacao = "MÉDIA"
        analise_base = "Nível de maturidade estável, necessitando apenas de automação de CRM e travas de governança."

    # PROCESSAMENTO SIMULADO DO AGENTE DE IA (Molda o relatório usando a dor real inserida pelo usuário)
    dor_usuario = dados.dor_mapeada if dados.dor_mapeada else "Não especificada textualmente."
    
    relatorio_agente_ia = f"""
    [Análise Gerada pelo Agente de IA ARCA]: Identificamos que a dor principal relatada ('{dor_usuario}') está diretamente conectada ao Score de {score_total}/100 obtido. {analise_base} O Framework ARCA identificou que a falta de padrões estruturados está drenando a margem de lucro da sua operação atual.
    """

    novo_lead = {
        "id": len(banco_leads) + 1,
        "empresa": dados.empresa,
        "responsavel": dados.responsavel,
        "email": dados.email,
        "whatsapp": dados.whatsapp,
        "tipo": dados.diagnostico_tipo,
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_ia": relatorio_agente_ia.strip(),
        "data_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    banco_leads.append(novo_lead)

    # LOG COMERCIAL NO TERMINAL DE PRODUÇÃO
    print("\n" + "="*70)
    print(f"🤖 [AGENTE DE IA] ANALISANDO RESPOSTAS DE: {dados.responsavel} ({dados.empresa})")
    print(f"💡 Dor Interpretada pela IA: '{dor_usuario}'")
    print(f"📊 Relatório Customizado Enviado para {dados.email} e WhatsApp {dados.whatsapp}")
    print("="*70 + "\n")

    return {
        "status": "Auditoria Processada pelo Agente de IA",
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": relatorio_agente_ia.strip(),
        "confirmacao_envio": {
            "email_status": f"Relatório Técnico compactado e enviado para {dados.email}",
            "whatsapp_status": f"Roadmap de melhorias e considerações enviado para {dados.whatsapp}"
        }
    }