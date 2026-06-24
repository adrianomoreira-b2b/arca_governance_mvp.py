from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("API_VERSION", "2.0.0")
TITLE = os.getenv("PROJECT_TITLE", "ARCA Governance")

app = FastAPI(title=TITLE, version=VERSION)

banco_leads = []

# Modelo de entrada de dados preparado para receber as notas por pilares
class DiagnosticoPilares(BaseModel):
    empresa: str = Field(..., example="Empresa Exemplo LTDA")
    responsavel: str = Field(..., example="Adriano Moreira")
    email: str = Field(..., example="diretoria@empresa.com.br")
    whatsapp: str = Field(..., example="11999999999")
    area_desejada: str = Field(..., description="MARKETING_VENDAS, FISCAL_TRIBUTARIO, GESTION_TIMES ou TECNOLOGIA")
    pilar_icp: int = Field(..., description="Pontuação 0, 5 ou 10")
    pilar_processos: int = Field(..., description="Pontuação 0, 5 ou 10")
    pilar_metricas: int = Field(..., description="Pontuação 0, 5 ou 10")
    dor_mapeada: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def carregar_aplicativo_visual():
    caminho_html = os.path.join("templates", "index.html")
    if not os.path.exists(caminho_html):
        return "<h1>Erro: templates/index.html não encontrado.</h1>"
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return HTMLResponse(content=arquivo.read())

@app.post("/diagnostico/processar/pilares")
def processar_diagnostico_pilares(dados: DiagnosticoPilares):
    # Cálculo Automatizado do Score ARCA (Máximo de 30 pontos convertidos para escala de 0 a 100)
    pontos_totais = dados.pilar_icp + dados.pilar_processos + dados.pilar_metricas
    score_calculado = int((pontos_totais / 30) * 100)
    
    # Definição de prioridade comercial
    if score_calculado <= 40:
        prioridade = "CRÍTICA"
        status_msg = "Risco Operacional Alto detectado."
    elif score_calculado <= 75:
        prioridade = "ALTA"
        status_msg = "Oportunidade de melhoria estrutural de média urgência."
    else:
        prioridade = "MÉDIA"
        status_msg = "Processos em conformidade regulatória básica."

    novo_registro = {
        "id": len(banco_leads) + 1,
        "empresa": dados.empresa,
        "responsavel": dados.responsavel,
        "email": dados.email,
        "whatsapp": dados.whatsapp,
        "area": dados.area_desejada,
        "score_arca": score_calculado,
        "prioridade": prioridade,
        "data_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    banco_leads.append(novo_registro)

    # SIMULAÇÃO DE DISPARO DE DISPARO EXTERNO (WHATSAPP/EMAIL)
    print("\n" + "="*60)
    print(f"🚨 [DISPARO AUTOMÁTICO] ENVIANDO DISGNÓSTICO PARA O WHATSAPP: {dados.whatsapp}")
    print(f"📧 ENVIANDO RELATÓRIO EXECUTIVO PARA O E-MAIL: {dados.email}")
    print(f"🏢 Registro de Empresa: {dados.empresa} | Score Calculado: {score_calculado}/100")
    print("="*60 + "\n")

    return {
        "status": "Diagnóstico Calculado com Sucesso",
        "score_arca": f"{score_calculado}/100",
        "classificacao": prioridade,
        "mensagem_analise": status_msg,
        "envio_canais": {
            "whatsapp_status": f"Enviado para {dados.whatsapp}",
            "email_status": f"Enviado para {dados.email}"
        }
    }