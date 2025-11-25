# core/llm_langchain_adapter.py
"""
Adaptador LangChain para integração com LLM Gemini.

CORREÇÕES APLICADAS:
1. Tratamento robusto para resposta vazia do LLM
2. Logging detalhado para debug
3. Fallback para mensagem padrão quando content está vazio
4. Tratamento de erros de API key
"""

from typing import Any, List, Optional, Dict
import json
import logging

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    FunctionMessage,
    ToolMessage,
    ToolCall,
    AIMessageChunk,
)
from langchain_core.outputs import (
    ChatResult,
    ChatGeneration,
    ChatGenerationChunk,
)

from core.llm_base import BaseLLMAdapter


# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def _clean_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove a chave 'anyOf' de um dicionário JSON Schema, recursivamente.
    A API Gemini não suporta 'anyOf' diretamente.
    """
    cleaned_schema = {}
    for key, value in schema.items():
        if key == "anyOf":
            # Ignorar 'anyOf' completamente
            continue
        elif isinstance(value, dict):
            cleaned_schema[key] = _clean_json_schema(value)
        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    cleaned_list.append(_clean_json_schema(item))
                else:
                    cleaned_list.append(item)
            cleaned_schema[key] = cleaned_list
        else:
            cleaned_schema[key] = value
    return cleaned_schema


class CustomLangChainLLM(BaseChatModel):
    """
    Adaptador customizado do LangChain para usar com GeminiLLMAdapter.
    
    CORREÇÕES:
    - Tratamento de resposta vazia
    - Logging detalhado
    - Fallback messages
    """
    
    llm_adapter: BaseLLMAdapter
    tools: Optional[List[Any]] = None

    @property
    def _llm_type(self) -> str:
        return "custom_llm"

    def __init__(self, llm_adapter: BaseLLMAdapter, **kwargs: Any):
        super().__init__(llm_adapter=llm_adapter, **kwargs)

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ) -> "CustomLangChainLLM":
        """Bind tools to the model."""
        new_instance = self.__class__(llm_adapter=self.llm_adapter, **kwargs)
        new_instance.tools = tools
        return new_instance

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Gera resposta usando o LLM adapter.
        
        CORREÇÕES:
        1. Log detalhado das mensagens e resposta
        2. Tratamento de resposta vazia
        3. Fallback para mensagem padrão
        """
        
        # =====================================================================
        # CORREÇÃO: Log das mensagens de entrada para debug
        # =====================================================================
        logger.debug(f"_generate chamado com {len(messages)} mensagens")
        
        # Convert LangChain messages to a generic dictionary format
        generic_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                generic_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                if msg.tool_calls:
                    processed_tool_calls = []
                    for tc in msg.tool_calls:
                        tc_dict = tc if isinstance(tc, dict) else tc.dict()
                        processed_tool_calls.append({
                            "id": tc_dict.get("id"),
                            "type": "function",
                            "function": {
                                "name": tc_dict.get("name"),
                                "arguments": json.dumps(tc_dict.get("args", {})),
                            },
                        })
                    generic_messages.append(
                        {
                            "role": "model",
                            "content": msg.content,
                            "tool_calls": processed_tool_calls,
                        }
                    )
                else:
                    generic_messages.append(
                        {"role": "model", "content": msg.content}
                    )
            elif isinstance(msg, SystemMessage):
                generic_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, FunctionMessage):
                generic_messages.append(
                    {
                        "role": "user",
                        "function_call": {
                            "name": msg.name,
                            "response": {"content": str(msg.content)}
                        }
                    }
                )
            elif isinstance(msg, ToolMessage):
                tool_name = msg.name
                if not tool_name or tool_name == "":
                    if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                        tool_name = msg.tool_call_id.replace("call_", "")
                    else:
                        tool_name = "unknown_tool"

                generic_messages.append(
                    {
                        "role": "user",
                        "function_call": {
                            "name": tool_name,
                            "response": {"content": str(msg.content)}
                        }
                    }
                )
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")

        # Process tools
        tools_to_pass = getattr(self, 'tools', None) or kwargs.get("tools")
        if tools_to_pass:
            generic_tools_declarations = []
            for tool in tools_to_pass:
                if hasattr(tool, 'name') and hasattr(tool, 'description') and hasattr(tool, 'args'):
                    required_params = [
                        param for param, details in tool.args.items() 
                        if details.get("default") is None and details.get("type") != "null"
                    ]

                    processed_args = {}
                    for param, details in tool.args.items():
                        param_details = details.copy()
                        if "default" in param_details:
                            del param_details["default"]
                        if "title" in param_details:
                            del param_details["title"]
                        processed_args[param] = param_details

                    cleaned_processed_args = _clean_json_schema(processed_args)

                    generic_tools_declarations.append(
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": "object",
                                "properties": cleaned_processed_args,
                                "required": required_params,
                            },
                        }
                    )
                elif isinstance(tool, dict) and "name" in tool and "description" in tool and "parameters" in tool:
                    generic_tools_declarations.append(tool)
                else:
                    logger.warning(f"Unexpected tool format encountered: {type(tool)} - {tool}")
                    if hasattr(tool, 'name') and hasattr(tool, 'description'):
                         generic_tools_declarations.append(
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "parameters": {"type": "object", "properties": {}},
                                }
                        )
                    else:
                        raise ValueError(f"Unsupported tool object: {tool}")

            tools_to_pass = {"function_declarations": generic_tools_declarations}
        else:
            tools_to_pass = None

        # =====================================================================
        # Chamar o LLM Adapter
        # =====================================================================
        logger.debug(f"Chamando llm_adapter.get_completion com {len(generic_messages)} mensagens")
        
        llm_response = self.llm_adapter.get_completion(
            messages=generic_messages, tools=tools_to_pass
        )

        # =====================================================================
        # CORREÇÃO: Log detalhado da resposta do LLM
        # =====================================================================
        logger.info(f"Resposta do LLM Adapter: {llm_response}")

        # =====================================================================
        # CORREÇÃO: Tratamento de erro
        # =====================================================================
        if "error" in llm_response:
            error_msg = llm_response['error']
            logger.error(f"Erro do LLM Adapter: {error_msg}")
            
            # Verificar se é erro de API key
            error_lower = str(error_msg).lower()
            if "403" in error_lower or "leaked" in error_lower or "api key" in error_lower:
                raise Exception(
                    f"Erro de autenticação com o Gemini: {error_msg}. "
                    f"Por favor, verifique se sua API key está válida."
                )
            
            raise Exception(f"LLM Adapter Error: {error_msg}")

        # =====================================================================
        # CORREÇÃO: Extrair content com tratamento de resposta vazia
        # =====================================================================
        content = llm_response.get("content")
        tool_calls_data = llm_response.get("tool_calls")
        warning = llm_response.get("warning")
        
        # Log de warning se houver
        if warning:
            logger.warning(f"Warning do LLM: {warning}")

        # =====================================================================
        # CORREÇÃO PRINCIPAL: Tratamento de content vazio
        # =====================================================================
        if content is None:
            content = ""
            logger.warning("LLM retornou content=None, usando string vazia")
        
        # Verificar se content está vazio E não há tool_calls
        content_is_empty = not content or not str(content).strip()
        has_tool_calls = tool_calls_data and len(tool_calls_data) > 0
        
        if content_is_empty and not has_tool_calls:
            logger.warning(
                f"⚠️ LLM retornou resposta vazia sem tool_calls! "
                f"Response: {llm_response}"
            )
            
            # =====================================================================
            # CORREÇÃO: Usar mensagem de fallback em vez de string vazia
            # =====================================================================
            content = (
                "Não foi possível processar sua solicitação no momento. "
                "Por favor, tente reformular sua pergunta."
            )
            logger.info(f"Usando mensagem de fallback: {content}")

        # =====================================================================
        # Processar tool_calls se houver
        # =====================================================================
        lc_tool_calls = []
        if tool_calls_data:
            logger.debug(f"Processando {len(tool_calls_data)} tool_calls")
            for tc_data in tool_calls_data:
                try:
                    args = json.loads(tc_data["function"]["arguments"])
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Erro ao parsear argumentos da tool: {e}")
                    args = {
                        "error": "Argumentos em formato JSON inválido",
                        "received": tc_data["function"]["arguments"],
                    }

                lc_tool_calls.append(
                    ToolCall(
                        name=tc_data["function"]["name"], 
                        args=args, 
                        id=tc_data["id"]
                    )
                )
            
            # Se tem tool_calls, o content deve ser vazio para o LangChain funcionar corretamente
            if lc_tool_calls:
                content = ""
                logger.debug(f"Tool calls detectadas, content definido como vazio")

        # =====================================================================
        # Criar AIMessage e retornar
        # =====================================================================
        ai_message = AIMessage(content=content, tool_calls=lc_tool_calls)
        
        logger.debug(
            f"Retornando AIMessage com content={content[:100] if content else 'vazio'}... "
            f"e {len(lc_tool_calls)} tool_calls"
        )

        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        raise NotImplementedError(
            "CustomLangChainLLM does not support async generation yet."
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Streaming - delega para _generate.
        
        CORREÇÃO: Tratamento de erro adicionado.
        """
        try:
            chat_result = self._generate(messages, stop, run_manager, **kwargs)
            
            if not chat_result.generations:
                logger.warning("_generate retornou sem generations")
                # Criar uma generation de fallback
                fallback_message = AIMessage(
                    content="Não foi possível gerar uma resposta.",
                    tool_calls=[]
                )
                yield ChatGenerationChunk(
                    message=AIMessageChunk(
                        content=fallback_message.content,
                        tool_calls=fallback_message.tool_calls
                    )
                )
                return
            
            generation = chat_result.generations[0]
            ai_message = generation.message

            message_chunk = AIMessageChunk(
                content=ai_message.content, 
                tool_calls=ai_message.tool_calls
            )

            yield ChatGenerationChunk(message=message_chunk)
            
        except Exception as e:
            logger.error(f"Erro no _stream: {e}", exc_info=True)
            
            # Yield uma mensagem de erro em vez de propagar a exceção
            error_message = AIMessageChunk(
                content=f"Erro ao processar: {str(e)}",
                tool_calls=[]
            )
            yield ChatGenerationChunk(message=error_message)
