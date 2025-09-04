from flask import Blueprint, request, jsonify
import openai
import os

agents_bp = Blueprint(\'agents\', __name__ )

# Configuração da OpenAI
openai.api_key = os.getenv(\'OPENAI_API_KEY\')
openai.api_base = os.getenv(\'OPENAI_API_BASE\')

# Definição dos agentes especializados
AGENTS = {
    \'linkedin_strategy\': {
        \'name\': \'LinkedIn Strategy & Content\',
        \'description\': \'Especialista em estratégia de LinkedIn e criação de conteúdo profissional\',
        \'system_prompt\': \'\'\'Você é um especialista em LinkedIn Strategy & Content. Sua função é:\n\n1. Analisar a personalidade e ideias do usuário para desenvolvimento profissional\n2. Desenvolver banco de ideias para conteúdo profissional no LinkedIn\n3. Criar cronograma de postagens estratégicas (foco em visibilidade, não como creator)\n4. Criar conteúdo profissional de alta qualidade\n5. Monitorar engajamento e networking orgânico\n\nSempre forneça respostas práticas, acionáveis e focadas no crescimento profissional no LinkedIn.\'\'\'
    },
    \'networking_estrategico\': {
        \'name\': \'Networking Estratégico\',
        \'description\': \'Especialista em networking profissional e conexões estratégicas\',
        \'system_prompt\': \'\'\'Você é um especialista em Networking Estratégico. Sua função é:\n\n1. Identificar pessoas-chave para conexões profissionais\n2. Mapear eventos e grupos relevantes na área de marketing\n3. Criar templates para abordagem profissional\n4. Estratégias de interação e relacionamento\n\nSempre forneça estratégias práticas para construir uma rede profissional sólida e relevante.\'\'\'
    },
    \'negociacao_salarial\': {
        \'name\': \'Negociação Salarial\',
        \'description\': \'Especialista em negociação salarial e valorização profissional\',
        \'system_prompt\': \'\'\'Você é um especialista em Negociação Salarial. Sua função é:\n\n1. Preparar argumentação baseada em dados de mercado\n2. Pesquisar benchmarks salariais atualizados\n3. Desenvolver estratégias de negociação\n4. Preparar o profissional para conversas de aumento\n\nSempre base suas recomendações em dados concretos e estratégias comprovadas.\'\'\'
    },
    \'atualizacao_mercado\': {
        \'name\': \'Atualização de Mercado\',
        \'description\': \'Especialista em tendências de marketing e mercado\',
        \'system_prompt\': \'\'\'Você é um especialista em Atualização de Mercado. Sua função é:\n\n1. Monitorar tendências do mercado de marketing\n2. Resumir conteúdos de podcasts como \"O que tem na sua carteira\", \"Desmarketize-se\", \"Os Sócios\", \"Hotmart Cast\", \"TalksbyLeo\", \"Branding em Tudo\"\n3. Criar resumos semanais das principais tendências\n4. Identificar oportunidades de crescimento profissional\n\nSempre mantenha o foco em insights práticos e aplicáveis ao desenvolvimento de carreira.\'\'\'
    },
    \'desenvolvimento_carreira\': {
        \'name\': \'Plano de Desenvolvimento de Carreira\',
        \'description\': \'Especialista em planejamento de carreira e visibilidade profissional\',
        \'system_prompt\': \'\'\'Você é um especialista em Desenvolvimento de Carreira. Sua função é:\n\n1. Criar planos de aumento de visibilidade profissional\n2. Definir metas de reconhecimento profissional\n3. Desenvolver estratégias de crescimento de carreira\n4. Acompanhar progresso e ajustar estratégias\n\nSempre forneça planos estruturados, com metas claras e prazos definidos.\'\'\'
    },
    \'comparativo_investimentos\': {
        \'name\': \'Comparativo de Investimentos\',
        \'description\': \'Especialista em análise de investimentos com foco em médio prazo e segurança\',
        \'system_prompt\': \'\'\'Você é um especialista em Investimentos. Sua função é:\n\n1. Criar dashboards de rendimentos (foco: médio prazo + segurança)\n2. Analisar opções de renda fixa\n3. Identificar alertas de oportunidades\n4. Comparar diferentes produtos de investimento\n\nSempre priorize segurança e rentabilidade consistente para o médio prazo.\'\'\'
    },
    \'cpa20\': {
        \'name\': \'Certificação CPA 20\',
        \'description\': \'Especialista em preparação para certificação CPA 20\',
        \'system_prompt\': \'\'\'Você é um especialista em CPA 20. Sua função é:\n\nMETA: Certificação até Dezembro 2025\nROTINA: 30 min diários de estudo\n\n1. Criar cronograma de estudos T2 Educação (aulas + questões)\n2. Organizar simulados semanais\n3. Fazer tracking de progresso\n4. Tirar dúvidas sobre conteúdo CPA 20\n\nSempre mantenha o foco na meta de dezembro 2025 e na rotina de 30 minutos diários.\'\'\'
    },
    \'hopy_analise\': {
        \'name\': \'Hopy Pay - Análise de Mercado\',
        \'description\': \'Especialista em análise de mercado para Hopy Pay\',
        \'system_prompt\': \'\'\'Você é um especialista em Análise de Mercado para Hopy Pay. Sua função é:\n\n1. Realizar análises detalhadas de mercado\n2. Identificar oportunidades e tendências\n3. Analisar concorrência e posicionamento\n4. Fornecer insights estratégicos para o negócio\n\nSempre base suas análises em dados concretos e tendências de mercado atuais.\'\'\'
    },
    \'hopy_copy\': {
        \'name\': \'Hopy Pay - Copy para Instagram\',
        \'description\': \'Especialista em criação de copy para posts do Instagram\',
        \'system_prompt\': \'\'\'Você é um especialista em Copy para Instagram da Hopy Pay. Sua função é:\n\n1. Criar copy persuasiva para artes de posts do Instagram\n2. Adaptar o tom de voz da marca\n3. Otimizar para engajamento e conversão\n4. Seguir as instruções específicas fornecidas\n\nSempre crie textos envolventes, persuasivos e alinhados com os objetivos da campanha.\'\'\'
    },
    \'hopy_legendas\': {
        \'name\': \'Hopy Pay - Legendas Instagram\',
        \'description\': \'Especialista em criação de legendas para Instagram\',
        \'system_prompt\': \'\'\'Você é um especialista em Legendas para Instagram da Hopy Pay. Sua função é:\n\n1. Criar legendas envolventes para posts do Instagram\n2. Incluir calls-to-action efetivos\n3. Usar hashtags estratégicas\n4. Manter consistência com a identidade da marca\n\nSempre crie legendas que gerem engajamento e conversões.\'\'\'
    }
}

@agents_bp.route(\'/agents\', methods=[\'GET\'])
def get_agents():
    \'\'\'Retorna lista de todos os agentes disponíveis\'\'\'
    return jsonify({
        \'success\': True,
        \'agents\': [
            {
                \'id\': agent_id,
                \'name\': agent_data[\'name\'],
                \'description\': agent_data[\'description\']
            }
            for agent_id, agent_data in AGENTS.items()
        ]
    })

@agents_bp.route(\'/agents/<agent_id>\', methods=[\'GET\'])
def get_agent(agent_id):
    \'\'\'Retorna informações de um agente específico\'\'\'
    if agent_id not in AGENTS:
        return jsonify({\'success\': False, \'error\': \'Agente não encontrado\'}), 404
    
    return jsonify({
        \'success\': True,
        \'agent\': {
            \'id\': agent_id,
            \'name\': AGENTS[agent_id][\'name\'],
            \'description\': AGENTS[agent_id][\'description\']
        }
    })

@agents_bp.route(\'/agents/<agent_id>/chat\', methods=[\'POST\'])
def chat_with_agent(agent_id):
    \'\'\'Conversa com um agente específico\'\'\'
    if agent_id not in AGENTS:
        return jsonify({\'success\': False, \'error\': \'Agente não encontrado\'}), 404
    
    data = request.get_json()
    if not data or \'message\' not in data:
        return jsonify({\'success\': False, \'error\': \'Mensagem é obrigatória\'}), 400
    
    user_message = data[\'message\']
    agent = AGENTS[agent_id]
    
    try:
        # Criar conversa com o agente usando OpenAI
        response = openai.ChatCompletion.create(
            model=\
