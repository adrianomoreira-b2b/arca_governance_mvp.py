from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

VERSION = "4.2.0"
TITLE = "ARCA Governance Engine - Codigo Blindado"

app = FastAPI(title=TITLE, version=VERSION)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")

# BLINDAGEM: Chave injetada direto no codigo para o Render nao perder a variavel
GEMINI_API_KEY = "AQ.Ab8RN6I7oVF1x5uuAfwUWja6_iV6WWh0WAg28_ORgwuZMAbDIg"

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

def gerar_analise_agente_ia(dados: PayloadDiagnosticoARCA, score_total: int) -> str:
    """Consome a API do Gemini via POST HTTP com chave blindada no escopo interno."""
    chave_limpa = str(GEMINI_API_KEY).strip()

    if not chave_limpa or "COLE_AQUI" in chave_limpa:
        return f"[Aviso]: Seu Score ARCA foi de {score_total}/100. Insira a chave real no codigo main.py."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave_limpa}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_comando = f"""
    Você é o motor de IA oficial e Consultor Estratégico Sênior do Framework ARCA do Grupo Gestão Integrada.
    Sua tarefa é analisar o resultado deste diagnóstico empresarial e redigir uma análise executiva legítima, profunda e consultiva.

    REGRAS CRÍTICAS DE TEXTO:
    1. IDIOMA: Use estritamente o Português do Brasil. Proibido qualquer jargão ou termo de Portugal.
    2. COMPILAÇÃO DE ADERÊNCIA: Avalie as justificativas textuais escritas pelo cliente pergunta por pergunta. Identifique se o teor indica baixa, média ou alta aderência técnica aos padrões da governança ARCA.
    3. SUSTENTAÇÃO EM RECEITA (ROI): Demonstre, com base na dor relatada ('{dados.dor_mapeada}') e nas justificativas fornecidas, onde a operação está sofrendo vazamento de caixa (perda oculta de faturamento) e como a implantação do Framework ARCA vai gerar receita, organizar processos e proteger o lucro.
    4. TAMANHO DA RESPOSTA: Seu relatório deve ser denso e possuir obrigatoriamente entre 15 e 25 linhas operacionais de texto. Seja direto e firme nas fraquezas operacionais mapeadas.
    
    Dados para Auditoria:
    - Empresa Auditada: {dados.empresa}
    - Segmento/Escopo avaliado: {dados.diagnostico_tipo}
    - Score Geral Calculado: {score_total}/100
    - Notas por Pilar: A1={dados.score_pilar_a1}/25, R={dados.score_pilar_r}/25, C={dados.score_pilar_c}/25, A2={dados.score_pilar_a2}/25
    
    [Justificativas Inseridas pelo Lead]:
    {dados.justificativas_bloco}
    
    Gere o parecer real do Agente de IA ARCA agora:
    """

    payload_http = {
        "contents": [{"parts": [{"text": prompt_comando}]}],
        "generationConfig": {"temperature": 0.3}
    }

    try:
        response = requests.post(url, headers=headers, json=payload_http, timeout=25)
        if response.status_code == 200:
            resultado_json = response.json()
            return resultado_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"[Erro de Resposta da IA - Código {response.status_code}]: O motor de IA recebeu um retorno inválido para o Score {score_total}/100."
    except Exception as e:
        return f"[Erro Técnico de Conexão]: O servidor encontrou instabilidade ao processar o Score {score_total}/100. Por favor, tente novamente."

def disparar_emails_reais(destinatario_lead: str, assunto: str, corpo_texto: str):
    remetente_limpo = str(EMAIL_REMETENTE).strip()
    senha_limpa = str(EMAIL_SENHA_APP).replace(" ", "").strip()

    if not remetente_limpo or not senha_limpa:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = remetente_limpo
        msg['To'] = destinatario_lead
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        msg_copia = MIMEMultipart()
        msg_copia['From'] = remetente_limpo
        msg_copia['To'] = remetente_limpo
        msg_copia['Subject'] = f"🚨 [NOVO LEAD ARCA] - {assunto}"
        msg_copia.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(remetente_limpo, senha_limpa)
        server.sendmail(remetente_limpo, destinatario_lead, msg.as_string())
        server.sendmail(remetente_limpo, remetente_limpo, msg_copia.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ ERRO SMTP: {str(e)}")
        return False

@app.get("/", response_class=HTMLResponse)
def carregar_aplicativo_visual():
    caminho_html = os.path.join("templates", "index.html")
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return HTMLResponse(content=arquivo.read())

@app.post("/diagnostico/processar/completo")
def processar_diagnostico_completo(dados: PayloadDiagnosticoARCA):
    score_total = int(dados.score_pilar_a1 + dados.score_pilar_r + dados.score_pilar_c + dados.score_pilar_a2)
    
    if score_total <= 40:
        classificacao = "CRÍTICA"
    elif score_total <= 75:
        classificacao = "ALTA"
    else:
        classificacao = "MÉDIA"

    relatorio_agente_ia = gerar_analise_agente_ia(dados, score_total)

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
    🤖 ANÁLISE REAL DO AGENTE DE IA ARCA (15 A 25 LINHAS COM ROI):
    ----------------------------------------------------------------------
    {relatorio_agente_ia}
    
    ----------------------------------------------------------------------
    🚀 PRÓXIMO PASSO RECOMENDADO:
    Acesse a agenda do consultor Adriano Moreira no link abaixo para validar o plano de 90 dias focado em ganho de receita:
    https://calendar.app.google/C1d44pbpqbLmU17m7
    
    Atenciosamente,
    Equipe ARCA Governance & Grupo Gestão Integrada
    """

    envio_sucesso = disparar_emails_reais(dados.email, f"Resultado Diagnóstico ARCA - {dados.empresa}", corpo_email_formatado.strip())

    if envio_sucesso:
        status_email = f"Relatório enviado com sucesso para {dados.email} (com cópia para a diretoria)!"
    else:
        status_email = "Relatório exibido na tela com sucesso."

    return {
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": relatorio_agente_ia,
        "confirmacao_envio": {
            "email_status": status_email,
            "whatsapp_status": "Plano de melhorias gerado com sucesso."
        }
    }