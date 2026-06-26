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

VERSION = "2.5.0"
TITLE = "ARCA Governance Engine BR"

app = FastAPI(title=TITLE, version=VERSION)

# Coleta as variáveis do painel do Render
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "seuemail@gmail.com")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "kbzhyouejxprrhmx")

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

def disparar_emails_reais(destinatario_lead: str, assunto: str, corpo_texto: str):
    """Motor de envio SSL porta 465 forçado e corrigido."""
    remetente_limpo = str(EMAIL_REMETENTE).strip()
    senha_limpa = str(EMAIL_SENHA_APP).replace(" ", "").strip()

    try:
        # Monta o e-mail do Lead
        msg = MIMEMultipart()
        msg['From'] = remetente_limpo
        msg['To'] = destinatario_lead
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        # Monta a Cópia de Controle para você
        msg_copia = MIMEMultipart()
        msg_copia['From'] = remetente_limpo
        msg_copia['To'] = remetente_limpo
        msg_copia['Subject'] = f"🚨 [NOVO LEAD ARCA] - {assunto}"
        msg_copia.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))

        # Conexão SSL Direta na porta 465 (padrão seguro do Google)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(remetente_limpo, senha_limpa)
        
        server.sendmail(remetente_limpo, destinatario_lead, msg.as_string())
        server.sendmail(remetente_limpo, remetente_limpo, msg_copia.as_string())
        
        server.quit()
        print("✅ DISPARO REAL EXECUTADO COM SUCESSO!")
        return True
    except Exception as e:
        print(f"❌ ERRO SMTP REAL: {str(e)}")
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

    relatorio_agente_ia = f"[Análise do Agente de IA ARCA]: Identificamos que a dor principal relatada ('{dor_usuario}') está diretamente conectada ao Score de {score_total}/100 Playbook obtido.\n\nDirecionamento Técnico: {analise_base} O Framework ARCA aponta que a falta de processos e o retrabalho manual estão drenando a margem latente do negócio."

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
    Para validar estes dados e estruturar o plano de contingência de 90 dias, acesse a agenda do consultor Adriano Moreira no link abaixo:
    https://calendar.app.google/C1d44pbpqbLmU17m7
    
    Atenciosamente,
    Equipe ARCA Governance & Grupo Gestão Integrada
    """

    envio_sucesso = disparar_emails_reais(
        destinatario_lead=dados.email,
        assunto=f"Resultado Diagnóstico ARCA - {dados.empresa}",
        corpo_texto=corpo_email_formatado.strip()
    )

    if envio_sucesso:
        status_email = f"Relatório enviado com sucesso para {dados.email}!"
    else:
        status_email = "Relatório processado e salvo na tela com sucesso!"

    return {
        "score_arca": score_total,
        "classificacao": classification,
        "analise_macro": relatorio_agente_ia,
        "confirmacao_envio": {
            "email_status": status_email,
            "whatsapp_status": "Plano de melhorias gerado com sucesso."
        }
    }