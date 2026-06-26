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

VERSION = "3.4.0"
TITLE = "ARCA Governance Engine - Conexão IA"

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
    """Motor de IA corrigido com carregamento forçado da chave de API."""
    chave_limpa = str(GEMINI_API_KEY).strip()

    if not chave_limpa or chave_limpa == "":
        return f"[Aviso de Configuração]: Seu Score ARCA foi de {score_total}/100. Adicione a chave GEMINI_API_KEY no painel do Render."

    try:
        # Configuração explícita da API Key antes da geração
        genai.configure(api_key=chave_limpa)
        
        prompt_comando = f"""
        Você é o motor de IA oficial e Consultor Estratégico do Framework ARCA do Grupo Gestão Integrada.
        Sua tarefa é analisar o resultado de um diagnóstico empresarial e redigir uma análise executiva legítima, profunda e personalizada.

        REGRAS CRÍTICAS DE TEXTO:
        1. IDIOMA: Use estritamente o Português do Brasil. Nunca use termos de Portugal.
        2. ANÁLISE COMPILADA: Avalie detalhadamente a dor do cliente: '{dados.dor_mapeada}'. Analise as justificativas reais inseridas por ele: '{dados.justificativas_bloco}'. Cruze tudo com o Score Geral de {score_total}/100.
        3. SUSTENTAÇÃO EM RECEITA (ROI): Mostre claramente onde a falta de processos, retrabalhos ou controles manuais está gerando vazamento de caixa e perda de faturamento latente. Diga como a metodologia ARCA estanca essa perda e gera retorno financeiro direto na receita operacional.
        4. TAMANHO DA RESPOSTA: Seu relatório deve ser denso e possuir obrigatoriamente entre 15 e 25 linhas operacionais de texto.
        
        Dados da Empresa {dados.empresa}:
        - Escopo: {dados.diagnostico_tipo}
        - Pontuação Geral: {score_total}/100
        - Pontuações por Pilar: A1={dados.score_pilar_a1}/25, R={dados.score_pilar_r}/25, C={dados.score_pilar_c}/25, A2={dados.score_pilar_a2}/25
        
        Escreva o parecer consultivo real agora:
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt_comando,
            generation_config={"temperature": 0.3}
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ FALHA DE AUTENTICAÇÃO GEMINI: {str(e)}")
        return f"[Erro Técnico de Conexão]: O servidor de IA encontrou instabilidade ao processar o Score {score_total}/100. Por favor, tente novamente."

def disparar_emails_reais(destinatario_lead: str, sender: str, corpo_texto: str):
    remetente_limpo = str(EMAIL_REMETENTE).strip()
    senha_limpa = str(EMAIL_SENHA_APP).replace(" ", "").strip()

    if not remetente_limpo or not senha_limpa:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = remetente_limpo
        msg['To'] = destinatario_lead
        msg['Subject'] = sender
        msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        msg_copia = MIMEMultipart()
        msg_copia['From'] = remetente_limpo
        msg_copia['To'] = remetente_limpo
        msg_copia['Subject'] = f"🚨 [NOVO LEAD ARCA] - {sender}"
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