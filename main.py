from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Definição de variáveis seguras com fallback caso o .env falhe
VERSION = os.getenv("API_VERSION", "2.0.0")
TITLE = os.getenv("PROJECT_TITLE", "ARCA Governance MVP - v2.0")
TICKET_MIN = os.getenv("TICKET_MIN", "2500")
TICKET_MAX = os.getenv("TICKET_MAX", "8000")

app = FastAPI(
    title=TITLE,
    description="Motor de Governança Comercial e Diagnósticos Automáticos Topo de Funil",
    version=VERSION
)

class LeadDiagnostico(BaseModel):
    empresa: str = Field(..., example="Contabilidade Alfa")
    responsavel: str = Field(..., example="Donizete Silva")
    frente_atuacao: str = Field(..., description="COMERCIAL, CONTABIL_1 ou CONTABIL_2", example="CONTABIL_1")
    usa_dominio: bool = Field(default=True)
    score_arca: int = Field(..., ge=0, le=100, description="Score gerado pelo app de diagnóstico", example=75)
    dor_mapeada: Optional[str] = Field(None, example="Gargalo no fechamento de Lucro Real")

@app.get("/")
def home():
    return {
        "produto": "ARCA Governance Engine",
        "versao": VERSION,
        "status": "Operacional",
        "frentes_suportadas": ["Frente Comercial B2B", "Frente Contábil 1 (Parcerias)", "Frente Contábil 2 (Clientes Finais)"],
        "timestamp": datetime.now()
    }

@app.post("/diagnostico/processar")
def processar_diagnostico(lead: LeadDiagnostico):
    frente = lead.frente_atuacao.upper()
    if frente not in ["COMERCIAL", "CONTABIL_1", "CONTABIL_2"]:
        raise HTTPException(status_code=400, detail="Frente de atuação inválida. Use: COMERCIAL, CONTABIL_1 ou CONTABIL_2.")

    if lead.score_arca >= 80:
        prioridade = "CRÍTICA (Risco Fiscal/Operacional Alto)"
        sugestao_upsell = "Oferecer imediatamente validação humana do plano de 90 dias com os diretores."
    elif lead.score_arca >= 50:
        prioridade = "ALTA (Oportunidade de Melhoria Estrutural)"
        sugestao_upsell = "Direcionar para agendamento de reunião de conversão."
    else:
        prioridade = "MÉDIA (Nutrição e Roadmap Automatizado)"
        sugestao_upsell = "Inserir fluxo de nutrição com materiais de apoio."

    ticket_ancoragem = f"Gratuito (Upsell de R$ {TICKET_MIN} a R$ {TICKET_MAX} para auditoria profunda)"

    return {
        "status": "Diagnóstico Processado com Sucesso",
        "lead": {
            "empresa": lead.empresa,
            "responsavel": lead.responsavel,
            "frente_identificada": frente
        },
        "entregaveis_gerados": {
            "score_arca": f"{lead.score_arca}/100",
            "relatorio_executivo": f"Análise macro baseada na dor: '{lead.dor_mapeada or 'Não informada'}'",
            "plano_90_dias": "Disponibilizado na página 2 do App",
            "roadmap": "Gerado dinamicamente"
        },
        "roteamento_comercial": {
            "prioridade_atendimento": prioridade,
            "estrategia_upsell": sugestao_upsell,
            "ancoragem_comercial": ticket_ancoragem
        }
    }