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

# Modelo de recepção de dados estruturado para a auditoria de 20 perguntas
class PayloadDiagnosticoARCA(BaseModel):
    empresa: str
    responsavel: str
    email: str
    whatsapp: str
    diagnostico_tipo: str  # VENDAS, FISCAL, GOVERNANCA, TECNOLOGIA
    score_pilar_a1: float  # Pontos acumulados no pilar Arquitetura (0 a 25)
    score_pilar_r: float   # Pontos acumulados no pilar Receita (0 a 25)
    score_pilar_c: float   # Pontos acumulados no pilar Execução (0 a 25)
    score_pilar_a2: float  # Pontos acumulados no pilar Aceleração (0 a 25)
    dor_mapeada: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def carregar_aplicativo_visual():
    """Retorna a interface do sistema lendo o arquivo HTML nativo."""
    caminho_html = os.path.join("templates", "index.html")
    if not os.path.exists(caminho_html):
        return "<h1>Erro Técnico: O arquivo templates/index.html não foi encontrado.</h1>"
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return HTMLResponse(content=arquivo.read())

@app.post("/diagnostico/processar/completo")
def processar_diagnostico_completo(dados: PayloadDiagnosticoARCA):
    # Soma matemática dos 4 blocos de pilares (Soma máxima = 100 pontos)
    score_total = int(dados.score_pilar_a1 + dados.score_pilar_r + dados.score_pilar_c + dados.score_pilar_a2)
    
    # Regra de Roteamento de Risco Comercial do Framework
    if score_total <= 40:
        classificacao = "CRÍTICA"
        analise_macro = "Operação Comercial desorganizada com vazamento de receita e perdas ocultas graves."
    elif score_total <= 75:
        classificacao = "ALTA"
        analise_macro = "Apresenta gargalos de processos e dependência severa de execução manual."
    else:
        classificacao = "MÉDIA"
        analise_macro = "Nível de maturidade estável, necessitando apenas de automação de CRM e travas de governança."

    novo_lead = {
        "id": len(banco_leads) + 1,
        "empresa": dados.empresa,
        "responsavel": dados.responsavel,
        "email": dados.email,
        "whatsapp": dados.whatsapp,
        "tipo": dados.diagnostico_tipo,
        "score_arca": score_total,
        "classificacao": classificacao,
        "data_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    banco_leads.append(novo_lead)

    # SIMULAÇÃO DE DISPAROS DE EMAIL E WHATSAPP COM BASE EM DADOS CONFIRMADOS
    print("\n" + "="*70)
    print(f"📧 [E-MAIL ENVIADO SEGURO] Destinatário: {dados.email}")
    print(f"📱 [WHATSAPP DISPARADO] Número: {dados.whatsapp}")
    print(f"🏢 Organização Auditada: {dados.empresa} | Responsável: {dados.responsavel}")
    print(f"📊 Relatório Gerado: Score {score_total}/100 | Classificação de Risco: {classificacao}")
    print("="*70 + "\n")

    return {
        "status": "Auditoria Processada com Sucesso",
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": analise_macro,
        "confirmacao_envio": {
            "email_status": f"Relatório Técnico compactado e enviado para {dados.email}",
            "whatsapp_status": f" Roadmap de melhorias e considerações enviado para {dados.whatsapp}"
        }
    }