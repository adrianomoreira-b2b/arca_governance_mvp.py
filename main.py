def gerar_analise_agente_ia(dados: PayloadDiagnosticoARCA, score_total: int) -> str:
    """
    Consome a API oficial do Gemini utilizando API Key via Query String.
    Compatível com chaves geradas no Google AI Studio.
    """

    chave_sistema = os.getenv("GEMINI_API_KEY", "").strip()

    # Validação da chave
    if not chave_sistema:
        return (
            f"[Aviso]: Seu Score ARCA foi de {score_total}/100. "
            f"A variável GEMINI_API_KEY não foi encontrada no Render."
        )

    # Logs de diagnóstico (visíveis nos logs do Render)
    print("=" * 80)
    print("INICIANDO CHAMADA GEMINI")
    print(f"Chave carregada: {'SIM' if chave_sistema else 'NÃO'}")
    print(f"Tamanho da chave: {len(chave_sistema)}")
    print(f"Prefixo da chave: {chave_sistema[:10]}...")
    print("=" * 80)

    # Endpoint oficial do Gemini
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={chave_sistema}"
    )

    prompt_comando = f"""
Você é o motor de IA oficial e Consultor Estratégico Sênior do Framework ARCA do Grupo Gestão Integrada.

Sua tarefa é analisar o resultado deste diagnóstico empresarial e redigir uma análise executiva legítima, profunda e consultiva.

REGRAS CRÍTICAS:

1. Utilize exclusivamente Português do Brasil.
2. Analise as justificativas fornecidas pelo cliente.
3. Identifique aderência técnica aos padrões do Framework ARCA.
4. Demonstre impactos financeiros e oportunidades de ROI.
5. Explique riscos operacionais e comerciais identificados.
6. A resposta deve possuir entre 15 e 25 linhas.
7. O texto deve ser executivo, consultivo e orientado à geração de receita.

DADOS DA AUDITORIA

Empresa: {dados.empresa}
Responsável: {dados.responsavel}
Escopo Avaliado: {dados.diagnostico_tipo}

Score Geral: {score_total}/100

Notas por Pilar:
- A1: {dados.score_pilar_a1}/25
- R: {dados.score_pilar_r}/25
- C: {dados.score_pilar_c}/25
- A2: {dados.score_pilar_a2}/25

Dor principal relatada:
{dados.dor_mapeada}

Justificativas registradas pelo cliente:
{dados.justificativas_bloco}

Gere agora o parecer executivo completo.
"""

    payload_http = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_comando
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
            json=payload_http,
            timeout=60
        )

        # Logs completos
        print("=" * 80)
        print(f"STATUS GOOGLE: {response.status_code}")
        print(f"RESPOSTA GOOGLE: {response.text}")
        print("=" * 80)

        # Resposta OK
        if response.status_code == 200:

            resultado_json = response.json()

            candidatos = resultado_json.get("candidates", [])

            if not candidatos:
                return (
                    f"[Erro IA]: O Gemini retornou sucesso, "
                    f"mas não gerou conteúdo para o Score {score_total}/100."
                )

            texto = (
                candidatos[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            )

            if texto:
                return texto

            return (
                f"[Erro IA]: O Gemini retornou uma estrutura vazia "
                f"para o Score {score_total}/100."
            )

        # Captura erro real do Google
        try:
            erro_google = response.json()
            mensagem_google = erro_google.get("error", {}).get(
                "message",
                response.text
            )
        except Exception:
            mensagem_google = response.text

        return (
            f"[Erro de Resposta da IA - Código {response.status_code}] "
            f"{mensagem_google}"
        )

    except requests.exceptions.Timeout:
        print("ERRO: Timeout na comunicação com Gemini.")

        return (
            "[Erro Técnico]: Tempo excedido na comunicação com o motor de IA."
        )

    except requests.exceptions.ConnectionError:
        print("ERRO: Falha de conexão com os servidores Google.")

        return (
            "[Erro Técnico]: Não foi possível conectar ao serviço de IA."
        )

    except Exception as e:
        print(f"ERRO INESPERADO GEMINI: {str(e)}")

        return (
            f"[Erro Técnico Interno]: {str(e)}"
        )