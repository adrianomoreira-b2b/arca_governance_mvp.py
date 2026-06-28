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

VERSION = "4.6.0"
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
        return "[ERRO] Variável GEMINI_API_KEY não encontrada no ambiente."

    # Modelo atualmente suportado pela API Gemini
    modelo = "gemini-2.0-flash"

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent?key={chave_sistema}"
    )

    prompt = f"""
Você é o Consultor Estratégico Sênior do Framework ARCA do Grupo Gestão Integrada.

Analise os dados abaixo e gere um relatório executivo consultivo.

REGRAS:
- Utilizar exclusivamente Português do Brasil.
- Produzir entre 15 e 25 linhas.
- Identificar riscos operacionais.
- Apresentar oportunidades de melhoria.
- Demonstrar potenciais ganhos financeiros e ROI.
- Ser objetivo, consultivo e executivo.

EMPRESA: {dados.empresa}
RESPONSÁVEL: {dados.responsavel}
TIPO DE DIAGNÓSTICO: {dados.diagnostico_tipo}

SCORE GERAL: {score_total}/100

PILARES:
A1 = {dados.score_pilar_a1}/25
R  = {dados.score_pilar_r}/25
C  = {dados.score_pilar_c}/25
A2 = {dados.score_pilar_a2}/25

DOR PRINCIPAL:
{dados.dor_mapeada}

JUSTIFICATIVAS:
{dados.justificativas_bloco}

Gere agora o parecer executivo.
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
            url=url,
            headers={
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        print("=" * 80)
        print("STATUS GEMINI:", response.status_code)
        print("RESPOSTA GEMINI:", response.text)
        print("=" * 80)

        if response.status_code != 200:
            return (
                f"[ERRO IA {response.status_code}]\n"
                f"{response.text}"
            )

        resposta = response.json()

        candidatos = resposta.get("candidates", [])

        if not candidatos:
            return "[ERRO IA] Nenhum conteúdo retornado."

        texto = (
            candidatos[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not texto:
            return "[ERRO IA] Resposta vazia."

        return texto.strip()

    except Exception as e:
        print("ERRO GEMINI:", str(e))
        return f"[ERRO TÉCNICO GEMINI] {str(e)}"

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

    if not remetente or not senha:
        print("Credenciais SMTP ausentes.")
        return False

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
            465,
            timeout=20
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

    if os.path.exists(caminho):

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return HTMLResponse(
                content=arquivo.read()
            )

    return HTMLResponse(
        content="""
        <html>
            <body>
                <h1>ARCA Governance Engine Online</h1>
            </body>
        </html>
        """
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

Score ARCA Calculado: {score_total}/100
Nível de Risco Comercial: {classificacao}

============================================================

ANÁLISE EXECUTIVA DO AGENTE ARCA

{relatorio_ia}

============================================================

Próximo passo recomendado:

https://calendar.app.google/C1d44pbpqbLmU17m7

Equipe ARCA Governance
Grupo Gestão Integrada
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
                "Relatório enviado com sucesso."
                if envio
                else "Falha no envio do e-mail."
            )
        }
    }
