from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("API_VERSION", "2.0.0")
TITLE = os.getenv("PROJECT_TITLE", "ARCA Governance MVP - v2.0")
TICKET_MIN = os.getenv("TICKET_MIN", "2500")
TICKET_MAX = os.getenv("TICKET_MAX", "8000")

app = FastAPI(title=TITLE, version=VERSION)

banco_leads = []

class LeadDiagnostico(BaseModel):
    empresa: str
    responsavel: str
    frente_atuacao: str
    usa_dominio: bool
    score_arca: int
    dor_mapeada: Optional[str] = None

# CORRIGIDO: ROTA PRINCIPAL LÊ O ARQUIVO DIRETAMENTE, CONTORNANDO O BUG DO PYTHON 3.14
@app.get("/", response_class=HTMLResponse)
def carregar_aplicativo_visual():
    """Retorna a página principal do App de Autodiagnóstico diretamente do arquivo local."""
    caminho_html = os.path.join("templates", "index.html")
    
    if not os.path.exists(caminip := caminho_html):
        return "<h1>Erro: O arquivo templates/index.html não foi encontrado.</h1>"
        
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        conteudo_html = arquivo.read()
        
    return HTMLResponse(content=conteudo_html)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/diagnostico/leads", response_model=List[dict])
def listar_leads():
    return banco_leads

@app.post("/diagnostico/processar")
def processar_diagnostico(lead: LeadDiagnostico):
    frente = lead.frente_atuacao.upper()
    if frente not in ["COMERCIAL", "CONTABIL_1", "CONTABIL_2"]:
        raise HTTPException(status_code=400, detail="Frente inválida.")

    if lead.score_arca >= 80:
        prioridade = "CRÍTICA (Risco Fiscal/Operacional Alto)"
        sugestao_upsell = "Oferecer imediatamente validação humana do plano de 90 dias com os diretores."
    elif lead.score_arca >= 50:
        prioridade = "ALTA (Oportunidade de Melhoria Estrutural)"
        sugestao_upsell = "Direcionar para agendamento de reunião de conversão."
    else:
        prioridade = "MÉDIA (Nutrição e Roadmap Automatizado)"
        sugestao_upsell = "Inserir fluxo de nutrição com materiais de apoio."

    # Algoritmo do Roadmap Dinâmico
    roadmap_dinamico = []
    plano_90_dias = {}

    if frente == "COMERCIAL":
        roadmap_dinamico = [
            "Fase 1 (Mês 1): Mapeamento de gargalos de qualificação de leads jurídicos.",
            "Fase 2 (Mês 2): Implementação de Playbooks e roteiros de conversão comercial.",
            "Fase 3 (Mês 3): Ativação de canais previsíveis de captação ativa de novos clientes."
        ]
        plano_90_dias = {
            "0-30 dias": "Definição clara do perfil de cliente ideal (ICP) e criação de scripts consultivos.",
            "31-60 dias": "Treinamento do time comercial e acompanhamento de taxas de rejeição na prospecção.",
            "61-90 dias": "Auditoria de reuniões de fechamento e implementação de travas de follow-up pós-proposta."
        }
    else:
        roadmap_dinamico = [
            "Fase 1 (Mês 1): Auditoria de parametrizações críticas e conformidade operacional.",
            "Fase 2 (Mês 2): Padronização dos fluxos internos de fechamento e checagem de compliance.",
            "Fase 3 (Mês 3): Otimização da produtividade do time e redução de retrabalhos manuais."
        ]
        if lead.usa_dominio:
            roadmap_dinamico.insert(1, "Ação Imediata: Ajuste avançado e parametrização do sistema Domínio para Lucro Real/Presumido.")

        plano_90_dias = {
            "0-30 dias": "Mapeamento dos processos manuais e identificação de riscos fiscais ocultos na apuração.",
            "31-60 dias": "Reestruturação das parametrizações contábeis e melhoria da qualidade operacional.",
            "61-90 dias": "Implementação do Score ARCA contínuo e treinamento em rotinas preventivas de compliance."
        }

    ticket_ancoragem = f"Gratuito (Upsell de R$ {TICKET_MIN} a R$ {TICKET_MAX} para auditoria profunda)"

    novo_registro = {
        "id": len(banco_leads) + 1,
        "empresa": lead.empresa,
        "responsavel": lead.responsavel,
        "frente": frente,
        "score_arca": lead.score_arca,
        "prioridade_comercial": prioridade,
        "data_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    banco_leads.append(novo_registro)

    print(f"\n🚨 [ALERTA] NOVO LEAD: {lead.empresa} | Score: {lead.score_arca} | Prioridade: {prioridade}\n")

    return {
        "status": "Diagnóstico Processado e Salvo com Sucesso",
        "lead": { "id_registro": novo_registro["id"], "empresa": lead.empresa, "responsavel": lead.responsavel, "frente_identificada": frente },
        "entregaveis_gerados": {
            "score_arca": f"{lead.score_arca}/100",
            "relatorio_executivo": f"Análise macro baseada na dor: '{lead.dor_mapeada or 'Não informada'}'",
            "plano_90_dias_personalizado": plano_90_dias,
            "roadmap_de_melhorias_dinamico": roadmap_dinamico
        },
        "roteamento_comercial": { "prioridade_atendimento": prioridade, "estrategia_upsell": sugestao_upsell, "ancoragem_comercial": ticket_ancoragem }
    }