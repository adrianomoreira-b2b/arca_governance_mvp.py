from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

VERSION = "3.2.0"
TITLE = "ARCA Governance Engine - IA Corrigida"

app = FastAPI(title=TITLE, version=VERSION)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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
    """Motor de IA corrigido passando o prompt diretamente no conteúdo para evitar falhas no Render."""
    if not GEMINI_API_KEY:
        print("⚠️ Chave GEMINI_API_KEY ausente.")
        return f"[Relatório Técnico ARCA]: Seu Score ARCA foi de {score_total}/100. Agende sua sessão para detalharmos o plano."

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Unificamos as regras de negócio e os dados do cliente em um único comando mestre
        prompt_completo = f"""
        Você é o motor especialista e consultor sênior do Framework ARCA, representando o Grupo Gestão Integrada.
        Sua missão é analisar as respostas estruturadas de um autodiagnóstico empresarial e gerar uma análise executiva profunda, realista e direta.

        REGRAS MANDATÓRIAS:
        1. IDIOMA: Use estritamente o Português do Brasil.
        2. ANÁLISE REAL: Leia atentamente a dor central relatada pelo cliente e as justificativas em texto preenchidas. Cruze isso com o Score Geral de {score_total}/100.
        3. SUSTENTAÇÃO FINANCEIRA (ROI): Demonstre onde a empresa está perdendo dinheiro (faturamento oculto) devido aos gargalos apontados e como a governança do Framework ARCA vai gerar receita e reter lucro.
        4. TAMANHO DA RESPOSTA: Escreva um texto denso e profissional que ocupe obrigatoriamente entre 15 e 25 linhas de conteúdo técnico.
        
        [Dados para Auditoria]:
        - Empresa: {dados.empresa}
        - Escopo: {dados.diagnostico_tipo}
        - Score Geral: {score_total}/100
        - Dor Comercial Relatada: '{dados.dor_mapeada}'
        - Justificativas preenchidas nas perguntas:
        {dados.justificativas_bloco}
        
        Gere o relatório executivo agora:
        """

        # Chamada direta e ultra compatível do modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt_completo,
            generation_config={"temperature": 0.3}
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ ERRO REAL NA API GEMINI: {str(e)}")
        return f"[Erro Técnico de Conexão]: O servidor de IA encontrou instabilidade ao processar o Score {score_total}/100. Por favor, tente novamente."

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
    🤖 ANÁLISE DO AGENTE DE IA ARCA (15 A 25 LINHAS COM ROI):
    ----------------------------------------------------------------------
    {relatorio_agente_ia}
    
    ----------------------------------------------------------------------
    🚀 PRÓXIMO PASSO RECOMENDADO:
    Acesse a agenda do consultor Adriano Moreira no link abaixo para validar o plano de 90 dias:
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