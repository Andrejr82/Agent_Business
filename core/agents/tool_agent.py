# core/agents/tool_agent.py
"""
Tool Agent - Agente responsável por executar ferramentas de BI.

CORREÇÕES APLICADAS:
1. Execução manual de ferramentas quando AgentExecutor não executa
2. Tratamento de tool_calls do Gemini
3. Melhor extração de respostas
"""

import logging
import json
from typing import Any, Dict, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.agents import AgentAction, AgentFinish

from core.llm_base import BaseLLMAdapter
from core.llm_gemini_adapter import GeminiLLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM
from core.utils.response_parser import parse_agent_response
from core.utils.chart_saver import save_chart

from core.tools.unified_data_tools import unified_tools
from core.tools.date_time_tools import date_time_tools
from core.tools.chart_tools import chart_tools


class ToolAgent:
    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.logger = logging.getLogger(__name__)
        self.llm_adapter = llm_adapter

        self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)

        self.tools = unified_tools + date_time_tools + chart_tools
        
        # Criar um dicionário de ferramentas para acesso rápido
        self.tools_dict = {tool.name: tool for tool in self.tools}
        
        self.agent_executor = self._create_agent_executor()
        self.logger.info("ToolAgent inicializado com adaptador Gemini.")

    def _create_agent_executor(self) -> AgentExecutor:
        """Cria e retorna um AgentExecutor com agente de ferramentas."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Você é um Agente de Negócios versátil e amigável, capaz de responder a perguntas sobre dados e gerar gráficos. "
                    "Sua principal função é usar as ferramentas disponíveis para responder de forma NATURAL e HUMANIZADA às perguntas do usuário.\n\n"

                    "## REGRAS DE COMUNICAÇÃO (MUITO IMPORTANTE!):\n"
                    "1. SEMPRE responda de forma NATURAL e CONVERSACIONAL, como um consultor de negócios falaria\n"
                    "2. NUNCA mencione nomes técnicos de colunas (como 'LUCRO R$', 'ITEM', 'VENDA R$') na resposta final\n"
                    "3. Use linguagem de negócios: 'lucro', 'vendas', 'produto', 'item', etc.\n"
                    "4. Seja direto e objetivo, mas amigável\n"
                    "5. Use formatação em Markdown para destacar valores importantes (negrito para números)\n"
                    "6. IMPORTANTE: Você DEVE SEMPRE fornecer uma resposta. NUNCA retorne uma resposta vazia.\n\n"

                    "EXEMPLOS DE RESPOSTAS HUMANIZADAS:\n"
                    "❌ ERRADO: 'O valor da coluna LUCRO R$ para o item com ITEM='9' é '18.49'.'\n"
                    "✅ CORRETO: 'O lucro do item 9 é **R$ 18,49**.'\n\n"

                    "❌ ERRADO: 'O valor da coluna SALDO para ITEM='5' é 150'\n"
                    "✅ CORRETO: 'O item 5 tem **150 unidades** em estoque.'\n\n"

                    "REGRA FUNDAMENTAL: SEMPRE que o usuário perguntar sobre dados de produtos/items, você DEVE usar a ferramenta `consultar_dados`. "
                    "NUNCA responda que não pode determinar algo sem antes tentar usar a ferramenta apropriada.\n\n"

                    "REGRA DE GRÁFICOS: Quando o usuário pedir um gráfico, use a ferramenta apropriada e SEMPRE forneça uma resposta confirmando a geração.\n\n"

                    "## COLUNAS DISPONÍVEIS NO DATASET:\n"
                    "Use os nomes EXATOS das colunas abaixo ao chamar as ferramentas (mas NÃO os mencione na resposta final!):\n\n"

                    "### Identificação:\n"
                    "- ITEM (número do item/produto)\n"
                    "- CODIGO (código do produto)\n"
                    "- DESCRIÇÃO (descrição do produto)\n"
                    "- FABRICANTE (fabricante do produto)\n"
                    "- GRUPO (grupo/categoria do produto)\n\n"

                    "### Valores Financeiros:\n"
                    "- VENDA R$ (valor total de vendas em reais)\n"
                    "- DESC. R$ (desconto em reais)\n"
                    "- CUSTO R$ (custo total em reais)\n"
                    "- LUCRO R$ (lucro total em reais)\n"
                    "- CUSTO UNIT R$ (custo unitário em reais)\n"
                    "- VENDA UNIT R$ (venda unitária em reais)\n\n"

                    "### Percentuais e Margens:\n"
                    "- LUCRO TOTAL % (percentual de lucro total)\n"
                    "- LUCRO UNIT % (percentual de lucro unitário)\n"
                    "- CLASSIFICACAO_MARGEM (classificação da margem de lucro)\n\n"

                    "### Quantidades:\n"
                    "- QTD (quantidade vendida)\n"
                    "- SALDO (saldo em estoque)\n"
                    "- QTD ULTIMA COMPRA (quantidade da última compra)\n\n"

                    "### Vendas Mensais:\n"
                    "- VENDA QTD JAN até VENDA QTD DEZ\n\n"

                    "### Análises e Métricas:\n"
                    "- VENDAS_TOTAL_ANO, VENDAS_MEDIA_MENSAL, DIAS_COBERTURA, STATUS_ESTOQUE\n\n"

                    "## REGRAS DE USO DAS FERRAMENTAS:\n\n"

                    "1. Para consultar dados específicos de um produto/item:\n"
                    "   - Use: `consultar_dados(coluna='ITEM', valor='X', coluna_retorno='NOME_COLUNA')`\n\n"

                    "2. Para gráficos de produto específico:\n"
                    "   - Use: `gerar_grafico_vendas_mensais_produto(codigo_produto=X)`\n\n"

                    "3. Para gráficos de vendas por grupo/categoria:\n"
                    "   - Use: `gerar_grafico_vendas_por_grupo(nome_grupo='NOME_DO_GRUPO')`\n\n"

                    "4. Para rankings:\n"
                    "   - Use: `gerar_ranking_produtos_mais_vendidos(top_n=N)`\n\n"

                    "5. Para dashboards completos:\n"
                    "   - Use: `gerar_dashboard_executivo()`\n\n"

                    "LEMBRE-SE: Sua resposta final deve ser NATURAL, AMIGÁVEL e SEM TERMOS TÉCNICOS!"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(
            llm=self.langchain_llm, tools=self.tools, prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

    def _execute_tool_manually(self, tool_name: str, tool_args: dict) -> Any:
        """
        Executa uma ferramenta manualmente quando o AgentExecutor não o faz.
        
        Args:
            tool_name: Nome da ferramenta
            tool_args: Argumentos da ferramenta
            
        Returns:
            Resultado da execução da ferramenta
        """
        self.logger.info(f"Executando ferramenta manualmente: {tool_name} com args: {tool_args}")
        
        if tool_name not in self.tools_dict:
            self.logger.error(f"Ferramenta não encontrada: {tool_name}")
            return {"error": f"Ferramenta '{tool_name}' não encontrada"}
        
        tool = self.tools_dict[tool_name]
        
        try:
            # Converter argumentos float para int se necessário (ex: codigo_produto)
            for key, value in tool_args.items():
                if isinstance(value, float) and value.is_integer():
                    tool_args[key] = int(value)
            
            result = tool.invoke(tool_args)
            self.logger.info(f"Resultado da ferramenta {tool_name}: {type(result)}")
            return result
        except Exception as e:
            self.logger.error(f"Erro ao executar ferramenta {tool_name}: {e}", exc_info=True)
            return {"error": str(e)}

    def _extract_response_from_intermediate_steps(
        self, intermediate_steps: list
    ) -> tuple:
        """
        Extrai resposta dos passos intermediários quando o output está vazio.
        
        Retorna: (response_type, final_output)
        """
        if not intermediate_steps:
            return None, None
            
        for step in reversed(intermediate_steps):
            if isinstance(step, tuple) and len(step) == 2:
                action, observation = step
                
                # Se a observação for um dicionário de gráfico
                if isinstance(observation, dict):
                    if observation.get("status") == "success" and "chart_data" in observation:
                        self.logger.info(f"Extraindo dados do gráfico da ferramenta: {action.tool}")
                        return "chart", observation["chart_data"]
                
                # Se a observação for uma string não vazia
                if isinstance(observation, str) and observation.strip():
                    self.logger.info(f"Extraindo resposta da ferramenta {action.tool}: {observation[:100]}...")
                    return "text", observation
        
        return None, None

    def _get_last_llm_response(self) -> dict:
        """
        Obtém a última resposta do LLM do adapter.
        Isso é necessário para acessar tool_calls quando o AgentExecutor não os processa.
        """
        # Acessar a última resposta através do adapter
        # Isso depende de como o adapter armazena a última resposta
        return getattr(self.langchain_llm, '_last_response', {})

    def process_query(
        self, query: str, chat_history: List[BaseMessage] = None
    ) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
        self.logger.info(f"Processando query com o Agente de Ferramentas: {query}")
        
        try:
            if chat_history is None:
                chat_history = []

            config = RunnableConfig(recursion_limit=10)

            self.logger.debug(
                f"Invocando agente com query: {query} "
                f"e chat_history: {chat_history}"
            )
            
            response = self.agent_executor.invoke(
                {"input": query, "chat_history": chat_history}, config=config
            )
            
            self.logger.debug(f"Resposta bruta do agente: {response}")
            self.logger.info(f"CONTEÚDO COMPLETO DA RESPOSTA DO AGENTE: {response}")

            final_output = response.get("output", "")
            intermediate_steps = response.get("intermediate_steps", [])
            response_type = "text"

            # =====================================================================
            # CORREÇÃO: Verificar se há tool_calls não executados
            # =====================================================================
            is_output_empty = not final_output or not str(final_output).strip()
            
            # Detectar intenção de gráfico na query do usuário
            chart_keywords = [
                "gráfico", "grafico", "chart", "plot", "visualizar", "visualização", 
                "dashboard", "pizza", "barras", "linha", "histograma"
            ]
            has_chart_intent = any(k in query.lower() for k in chart_keywords)
            
            # Se tem intenção de gráfico mas não retornou tipo chart, forçar retry
            if has_chart_intent and response_type != "chart" and not is_output_empty:
                # Verificar se alguma ferramenta foi chamada nos passos intermediários
                tools_called = [step[0].tool for step in intermediate_steps] if intermediate_steps else []
                chart_tools_called = any("grafico" in t or "dashboard" in t for t in tools_called)
                
                if not chart_tools_called:
                    self.logger.warning("Intenção de gráfico detectada mas nenhuma ferramenta de gráfico foi chamada. Forçando retry...")
                    
                    # Retry com instrução explícita
                    retry_query = (
                        f"{query}\n\n"
                        "SYSTEM_INSTRUCTION: O usuário pediu explicitamente um gráfico. "
                        "Você DEVE chamar uma ferramenta de geração de gráfico (ex: gerar_grafico_automatico). "
                        "NÃO responda apenas com texto. CHAME A FERRAMENTA AGORA."
                    )
                    
                    self.logger.info("Enviando query de retry para forçar gráfico...")
                    response = self.agent_executor.invoke(
                        {"input": retry_query, "chat_history": chat_history}, config=config
                    )
                    
                    final_output = response.get("output", "")
                    intermediate_steps = response.get("intermediate_steps", [])
                    
                    # Reavaliar se agora temos um gráfico
                    is_output_empty = not final_output or not str(final_output).strip()
            
            if is_output_empty:
                self.logger.warning(
                    f"Output do agente está vazio. "
                    f"Tentando extrair de intermediate_steps ({len(intermediate_steps)} passos)"
                )
                
                # Tentar extrair resposta dos passos intermediários
                extracted_type, extracted_output = self._extract_response_from_intermediate_steps(
                    intermediate_steps
                )
                
                if extracted_output:
                    self.logger.info(f"Resposta extraída com sucesso de intermediate_steps")
                    response_type = extracted_type or "text"
                    final_output = extracted_output
                else:
                    # =====================================================================
                    # CORREÇÃO PRINCIPAL: Executar ferramentas manualmente se necessário
                    # =====================================================================
                    self.logger.warning("Não foi possível extrair de intermediate_steps. Verificando tool_calls...")
                    
                    # Fazer uma nova chamada ao LLM para obter tool_calls
                    try:
                        # Converter mensagens para o formato do adapter
                        messages = [{"role": "user", "content": query}]
                        
                        # Preparar ferramentas no formato correto
                        tools_declarations = []
                        for tool in self.tools:
                            tools_declarations.append({
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": {
                                    "type": "object",
                                    "properties": tool.args if hasattr(tool, 'args') else {},
                                },
                            })
                        
                        tools_wrapper = {"function_declarations": tools_declarations}
                        
                        # Chamar o LLM diretamente
                        llm_response = self.llm_adapter.get_completion(
                            messages=messages, 
                            tools=tools_wrapper
                        )
                        
                        self.logger.info(f"Resposta direta do LLM: {llm_response}")
                        
                        # Se há tool_calls, executar manualmente
                        if "tool_calls" in llm_response and llm_response["tool_calls"]:
                            tool_call = llm_response["tool_calls"][0]
                            tool_name = tool_call["function"]["name"]
                            tool_args_str = tool_call["function"]["arguments"]
                            
                            try:
                                tool_args = json.loads(tool_args_str)
                            except json.JSONDecodeError:
                                tool_args = {}
                            
                            self.logger.info(f"Executando ferramenta: {tool_name} com args: {tool_args}")
                            
                            # Executar a ferramenta
                            tool_result = self._execute_tool_manually(tool_name, tool_args)
                            
                            # Verificar se é um gráfico
                            if isinstance(tool_result, dict):
                                if tool_result.get("status") == "success" and "chart_data" in tool_result:
                                    self.logger.info("Gráfico gerado com sucesso!")
                                    save_chart(tool_result["chart_data"])
                                    return {
                                        "type": "chart",
                                        "output": tool_result["chart_data"],
                                    }
                                elif "error" in tool_result:
                                    final_output = f"Erro ao executar a ferramenta: {tool_result['error']}"
                                else:
                                    # Formatar resultado como texto
                                    final_output = str(tool_result)
                            else:
                                final_output = str(tool_result) if tool_result else "Operação concluída."
                        
                        elif llm_response.get("content"):
                            final_output = llm_response["content"]
                            
                    except Exception as tool_error:
                        self.logger.error(f"Erro ao executar ferramenta manualmente: {tool_error}", exc_info=True)
                    
                    # Se ainda estiver vazio, retornar mensagem de erro
                    if not final_output or not str(final_output).strip():
                        self.logger.error(
                            "Não foi possível obter resposta após múltiplas tentativas"
                        )
                        return {
                            "type": "error",
                            "output": (
                                "Desculpe, não consegui processar sua consulta no momento. "
                                "Por favor, tente reformular sua pergunta de forma mais específica. "
                                "Por exemplo: 'Qual é o lucro do produto 10?' ou "
                                "'Mostre o gráfico de vendas do item 5'."
                            ),
                        }
            
            # =====================================================================
            # Processamento de gráficos (quando output não estava vazio)
            # =====================================================================
            if intermediate_steps and response_type == "text":
                for step in reversed(intermediate_steps):
                    if isinstance(step, tuple) and len(step) == 2:
                        action, observation = step
                        
                        if isinstance(observation, dict):
                            if observation.get("status") == "success" and "chart_data" in observation:
                                self.logger.info(f"Gráfico detectado da ferramenta: {action.tool}")
                                final_output = observation["chart_data"]
                                response_type = "chart"
                                save_chart(final_output)
                                break

            # Se for gráfico, retornar diretamente
            if response_type == "chart":
                return {
                    "type": "chart",
                    "output": final_output,
                }

            # Processar resposta de texto
            if isinstance(final_output, str) and final_output.strip():
                try:
                    parsed_type, processed = parse_agent_response(final_output)
                    return {
                        "type": parsed_type or "text",
                        "output": processed.get("output", final_output),
                    }
                except Exception as parse_error:
                    self.logger.warning(f"Erro no parse_agent_response: {parse_error}")
                    return {
                        "type": "text",
                        "output": final_output,
                    }
            
            # Fallback final
            return {
                "type": "text",
                "output": str(final_output) if final_output else "Não foi possível gerar uma resposta.",
            }

        except Exception as e:
            self.logger.error(f"Erro ao invocar o agente LangChain: {e}", exc_info=True)
            
            error_msg = str(e).lower()
            if "403" in error_msg or "api key" in error_msg or "leaked" in error_msg:
                return {
                    "type": "error",
                    "output": (
                        "Erro de autenticação com o serviço de IA. "
                        "Por favor, verifique se a API key está configurada corretamente."
                    ),
                }
            
            return {
                "type": "error",
                "output": (
                    "Desculpe, não consegui processar sua solicitação "
                    "no momento. Por favor, tente novamente ou reformule "
                    "sua pergunta."
                ),
            }


