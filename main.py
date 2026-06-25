from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("API_VERSION", "2.0.0")
TITLE = os.getenv("PROJECT_TITLE", "ARCA Governance Engine")

app = FastAPI(title=TITLE, version=VERSION)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP")

# MODELO DE DADOS ALINHADO EM 100% COM O FRONTEND
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
    justificativas_bloco: Optional[str] = ""  # Campo crucial de ligação

def disparar_emails_reais(destinatario_lead: str, assunto: str, corpo_texto: str):
    """Conexão segura via porta SSL 465 que evita bloqueios do Render."""
    if not EMAIL_REMETENTE or not EMAIL_SENHA_APP:
        print("⚠️ ALERTA: Credenciais de e-mail não configuradas no Render.")
        return False
    try:
        # Mensagem do Lead
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = destinatario_lead
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        # Sua Cópia de Controle
        msg_copia = MIMEMultipart()
        msg_copia['From'] = EMAIL_REMETENTE
        msg_copia['To'] = EMAIL_REMETENTE 
        msg_copia['Subject'] = f"🚨 [NOVO LEAD ARCA] - {assunto}"
        msg_copia.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        # Protocolo SSL Direto
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        server.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
        
        server.sendmail(EMAIL_REMETENTE, destinatario_lead, msg.as_string())
        server.sendmail(EMAIL_REMETENTE, EMAIL_REMETENTE, msg_copia.as_string())
        
        server.quit()
        print("✅ E-mails enviados com sucesso para o lead e diretoria!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão de e-mail SMTP: {str(e)}")
        return False

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
        analise_base = "Operação desorganizada com vazamento de faturamento e perdas ocultas graves."
    elif score_total <= 75:
        classificacao = "ALTA"
        analise_base = "Apresenta gargalos de processos e dependência severa de execução manual."
    else:
        classificacao = "MÉDIA"
        analise_base = "Nível de maturidade estável, necessitando apenas de automação fina e travas de governança."

    dor_usuario = dados.dor_mapeada if dados.dor_mapeada else "Não especificada."
    justificativas_enviadas = dados.justificativas_bloco if dados.justificativas_bloco else "Nenhuma justificativa inserida."

    relatorio_agente_ia = f"[Análise do Agente de IA ARCA]: Identificámos que a dor principal relatada ('{dor_usuario}') está diretamente conectada ao Score de {score_total}/100 obtido.\n\nDirecionamento Técnico: {analise_base} O Framework ARCA aponta que a falta de processos e o retrabalho manual estão a drenar a margem latente do negócio."

    corpo_email_formatado = f"""
    Olá, {dados.responsavel},
    
    Segue o relatório técnico estruturado gerado pelo Agente de IA do Framework ARCA para a empresa {dados.empresa}.
    
    ----------------------------------------------------------------------
    📊 DADOS CONSOLIDADOS DO LEAD
    ----------------------------------------------------------------------
    🏢 Organização: {dados.empresa}
    👤 Gestor Responsável: {dados.responsavel}
    📱 Canal WhatsApp: {dados.whatsapp}
    🎯 Escopo da Auditoria: {dados.diagnostico_tipo}
    
    📈 SCORE ARCA CALCULADO: {score_total} de 100 pontos.
    ⚠️ CLASSIFICAÇÃO DE RISCO: {classificacao}
    
    ----------------------------------------------------------------------
    🤖 ANÁLISE COMPORTAMENTAL DO AGENTE DE IA
    ----------------------------------------------------------------------
    {relatorio_agente_ia}
    
    ----------------------------------------------------------------------
    📝 JUSTIFICATIVAS INTERNAS RELATADAS PELO LEAD:
    ----------------------------------------------------------------------
    {justificativas_enviadas}
    
    ----------------------------------------------------------------------
    🚀 PRÓXIMO PASSO MANDATÓRIO:
    Para validar estes dados textuais e estruturar o plano de contingência de 90 dias, aceda à agenda do consultor Adriano Moreira no link abaixo:
    https://calendar.app.google/C1d44pbpqbLmU17m7
    
    Atenciosamente,
    Equipe ARCA Governance & Grupo Gestão Integrada
    """

    # Envia o e-mail real de forma isolada para não quebrar a tela do usuário se falhar
    envio_sucesso = disparar_emails_reais(
        destinatario_lead=dados.email,
        assunto=f"Resultado Diagnóstico ARCA - {dados.empresa}",
        corpo_texto=corpo_email_formatado.strip()
    )

    status_email = f"Relatório Técnico enviado para {dados.email}!" if envio_sucesso else "Exibido no ecrã com sucesso."

    return {
        "score_arca": score_total,
        "classificacao": classificacao,
        "analise_macro": relatorio_agente_ia,
        "confirmacao_envio": {
            "email_status": status_email,
            "whatsapp_status": "Roadmap de melhorias gerado."
        }
    }
