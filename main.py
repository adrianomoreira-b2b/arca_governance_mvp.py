from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# ==========================================================
# CONFIGURAÇÃO INICIAL
# ==========================================================

load_dotenv()

VERSION = "4.5.0"
TITLE = "ARCA Governance Engine - Produção Segura"

app = FastAPI(
    title=TITLE,
    version=VERSION
)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")

# ==========================================================
# MODELO DE DADOS
# ==========================================================

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
    dor_mapeada: Optional[str] = ""
    justificativas_bloco: Optional[str] = ""

# ==========================================================
# GEMINI
# ==========================================================

def gerar_analise_agente_ia(
    dados: PayloadDiagnosticoARCA,
    score_total: int
) -> str:

    chave_sistema = os.getenv("GEMINI_API_KEY", "").strip()

    if not chave_sistema:
        return "[ERRO] Variável GEMINI_API_KEY não encontrada."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={chave_sistema}"
    )

    prompt = f"""
Você é o Consultor Estratégico Sênior do Framework ARCA.

Analise os dados abaixo e gere um relatório executivo.

Regras:
- Utilizar Português do Brasil.
- Produzir entre 15 e 25 linhas.
- Identificar riscos operacionais.
- Demonstrar oportunidades de ROI.
- Apresentar recomendações práticas.

Empresa: {dados.empresa}
Responsável: {dados.responsavel}
Diagnóstico: {dados.diagnostico_tipo}

Score Geral: {score_total}/100

Pilares:
A1 = {dados.score_pilar_a1}/25
R = {dados.score_pilar_r}/25
C = {dados.score_pilar_c}/25
A2 = {dados.score_pilar_a2}/25

Dor principal:
{dados.dor_mapeada}

Justificativas:
{dados.justificativas_bloco}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1200
        }
    }

    try:

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        print("STATUS GEMINI:", response.status_code)
        print("RESPOSTA GEMINI:", response.text)

        if response.status_code != 200:
            return f"[ERRO IA {response.status_code}] {response.text}"

        resposta = response.json()

        return (
            resposta["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except Exception as e:
        print("ERRO GEMINI:", str(e))
        return f"[ERRO TÉCNICO] {str(e)}"

# ==========================================================
# SMTP
# ==========================================================

def disparar_emails_reais(
    destinatario: str,
    assunto: str,
    corpo: str
):

    remetente = EMAIL_REMETENTE.strip()
    senha = EMAIL_SENHA_APP.strip().replace(" ", "")

    try:

        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(
            MIMEText(corpo, "plain", "utf-8")
        )

        copia = MIMEMultipart()
        copia["From"] = remetente
        copia["To"] = remetente
        copia["Subject"] = f"NOVO LEAD ARCA - {assunto}"

        copia.attach(
            MIMEText(corpo, "plain", "utf-8")
        )

        servidor = smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        )

        servidor.login(
            remetente,
            senha
        )

        servidor.sendmail(
            remetente,
            destinatario,
            msg.as_string()
        )

        servidor.sendmail(
            remetente,
            remetente,
            copia.as_string()
        )

        servidor.quit()

        return True

    except Exception as e:
        print("ERRO SMTP:", str(e))
        return False

# ==========================================================
# ROTAS
# ==========================================================

@app.get("/", response_class=HTMLResponse)
def home():

    caminho = os.path.join(
        "templates",
        "index.html"
    )

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return HTMLResponse(
            content=arquivo.read()
        )

@app.get("/health")
def health():
    return {
        "status": "online",
        "versao": VERSION
    }

@app.post("/diagnostico/processar/completo")
def processar_diagnostico_completo(
    dados: PayloadDiagnosticoARCA
):

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

    relatorio_ia = gerar_analise_agente_ia(
        dados,
        score_total
    )

    corpo_email = f"""
Olá, {dados.responsavel}

Empresa: {dados.empresa}

Score ARCA: {score_total}/100

Classificação: {classificacao}

ANÁLISE EXECUTIVA

{relatorio_ia}

Agenda:
https://calendar.app.google/C1d44pbpqbLmU17m7

Equipe ARCA Governance
"""

    envio = disparar_emails_reais(
        dados.email,
        f"Resultado Diagnóstico ARCA - {dados.empresa}",
        corpo_email
    )

    return {
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": relatorio_ia,
        "confirmacao_envio": {
            "email_status": (
                "Enviado com sucesso"
                if envio else
                "Falha no envio"
            )
        }
    }