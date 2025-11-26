# core/llm_gemini_adapter.py
from typing import List, Dict, Any, Optional
import logging
import threading
import time
from queue import Queue
import json
from core.llm_base import BaseLLMAdapter
from core.config.config import Config

GEMINI_AVAILABLE = False

try:
    import google.generativeai as genai
    from google.api_core.exceptions import RetryError, InternalServerError
    from google.generativeai.types import FunctionDeclaration
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"Erro de importação do Gemini: {e}")


class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Adaptador para Google Gemini API.
    Implementa padrão similar ao OpenAI com retry automático e tratamento de erros.
    
    CORREÇÕES APLICADAS:
    1. Tratamento para resposta vazia do modelo
    2. Fallback para modelo mais estável
    3. Configuração de geração otimizada
    4. Logging detalhado para debug
    """

    # =========================================================================
    # CORREÇÃO: Modelos recomendados (em ordem de preferência)
    # =========================================================================
    RECOMMENDED_MODELS = [
        "gemini-1.5-flash",      # Mais estável e rápido
        "gemini-1.5-pro",        # Mais capaz
        "gemini-1.0-pro",        # Legado, mas estável
    ]
    
    # Modelos que podem causar problemas de resposta vazia
    PROBLEMATIC_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai não está instalado. "
                "Execute: pip install google-generativeai"
            )

        if not Config().GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Defina a variável de ambiente GEMINI_API_KEY ou adicione-a ao seu arquivo .streamlit/secrets.toml."
            )

        genai.configure(api_key=Config().GEMINI_API_KEY)

        self.model_name = Config().GEMINI_MODEL_NAME
        self.max_retries = 3
        self.retry_delay = 2
        
        # =====================================================================
        # CORREÇÃO: Alertar se usando modelo problemático
        # =====================================================================
        if self.model_name in self.PROBLEMATIC_MODELS:
            self.logger.warning(
                f"⚠️ O modelo '{self.model_name}' pode causar respostas vazias. "
                f"Recomendado usar: {self.RECOMMENDED_MODELS[0]}"
            )
        
        # =====================================================================
        # CORREÇÃO: Configuração de geração para evitar respostas vazias
        # =====================================================================
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "candidate_count": 1,
        }

        self.logger.info(f"Gemini adapter inicializado com modelo: {self.model_name}")

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Obtém completion da API Gemini com retry automático.

        Args:
            messages: Lista de mensagens no formato OpenAI-like
            tools: Dicionário opcional de ferramentas no formato Gemini

        Returns:
            Dicionário com resultado ou erro
            
        CORREÇÕES:
        1. Tratamento de resposta vazia
        2. Logging detalhado
        3. Fallback para mensagem padrão
        """
        for attempt in range(self.max_retries):
            try:
                q = Queue()

                def worker():
                    try:
                        gemini_messages = self._convert_messages(messages)
                        
                        if tools:
                            gemini_tools = self._convert_tools(tools)
                        else:
                            gemini_tools = []

                        # =====================================================
                        # CORREÇÃO: Usar generation_config
                        # =====================================================
                        model = genai.GenerativeModel(
                            model_name=self.model_name,
                            tools=gemini_tools if gemini_tools else None,
                            generation_config=self.generation_config,
                        )

                        chat_session = model.start_chat(history=gemini_messages[:-1])

                        self.logger.info(
                            f"Chamada Gemini (tentativa {attempt + 1}/"
                            f"{self.max_retries})"
                        )

                        # =====================================================
                        # CORREÇÃO: Adicionar instrução para garantir resposta
                        # =====================================================
                        last_message = gemini_messages[-1]["parts"]
                        
                        # Se for lista de dicts com 'text', extrair e adicionar instrução
                        if isinstance(last_message, list) and len(last_message) > 0:
                            if isinstance(last_message[0], dict) and "text" in last_message[0]:
                                original_text = last_message[0]["text"]
                                # Adicionar instrução apenas se for uma pergunta comum
                                if not any(x in original_text.lower() for x in ["function_response", "function_call"]):
                                    enhanced_parts = [{
                                        "text": f"{original_text}\n\n[INSTRUÇÃO: Forneça uma resposta completa e útil. Nunca retorne vazio.]"
                                    }]
                                    last_message = enhanced_parts

                        response = chat_session.send_message(last_message)

                        self.logger.info("Chamada Gemini concluída.")

                        tool_calls = []
                        content = ""
                        
                        # =====================================================
                        # CORREÇÃO: Tratamento robusto da resposta
                        # =====================================================
                        if response is None:
                            self.logger.warning("Gemini retornou response None")
                            q.put({
                                "content": "Não foi possível processar a solicitação.",
                                "warning": "response_none"
                            })
                            return
                        
                        if not response.candidates:
                            self.logger.warning("Gemini retornou sem candidates")
                            q.put({
                                "content": "Não foi possível gerar uma resposta.",
                                "warning": "no_candidates"
                            })
                            return
                        
                        candidate = response.candidates[0]
                        
                        # Verificar se o candidate foi bloqueado
                        if hasattr(candidate, 'finish_reason'):
                            finish_reason = str(candidate.finish_reason)
                            if "SAFETY" in finish_reason or "BLOCKED" in finish_reason:
                                self.logger.warning(f"Resposta bloqueada: {finish_reason}")
                                q.put({
                                    "content": "A resposta foi bloqueada por motivos de segurança.",
                                    "warning": f"blocked_{finish_reason}"
                                })
                                return
                        
                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if part.function_call:
                                    function_call = part.function_call
                                    tool_calls.append({
                                        "id": f"call_{function_call.name}",
                                        "function": {
                                            "arguments": json.dumps(dict(function_call.args)),
                                            "name": function_call.name,
                                        },
                                        "type": "function",
                                    })
                                    content = ""
                                    break
                                elif part.text:
                                    content = part.text
                                    break
                        
                        # =====================================================
                        # CORREÇÃO: Verificar se content está vazio
                        # =====================================================
                        if not tool_calls and (not content or not content.strip()):
                            self.logger.warning(
                                f"Gemini retornou content vazio na tentativa {attempt + 1}. "
                                f"Response: {response}"
                            )
                            
                            # Tentar extrair texto de outra forma
                            try:
                                if hasattr(response, 'text') and response.text:
                                    content = response.text
                                    self.logger.info(f"Content extraído via response.text: {content[:100]}...")
                            except Exception as text_error:
                                self.logger.warning(f"Não foi possível extrair via response.text: {text_error}")
                            
                            # Se ainda vazio, sinalizar para retry
                            if not content or not content.strip():
                                q.put({
                                    "error": "Resposta vazia do modelo",
                                    "retry": True,
                                    "warning": "empty_content"
                                })
                                return
                        
                        # Log do conteúdo para debug
                        if content:
                            self.logger.debug(f"Content recebido: {content[:200]}...")
                        
                        result = {"content": content}
                        if tool_calls:
                            result["tool_calls"] = tool_calls
                        
                        q.put(result)

                    except Exception as e:
                        error_msg = str(e).lower()

                        # Verificar se é erro de API key vazada/inválida
                        is_auth_error = any([
                            "403" in error_msg,
                            "api key" in error_msg,
                            "leaked" in error_msg,
                            "invalid" in error_msg and "key" in error_msg,
                        ])
                        
                        if is_auth_error:
                            self.logger.error(f"Erro de autenticação: {e}")
                            q.put({
                                "error": f"Erro: {e}",
                                "retry": False,
                                "auth_error": True
                            })
                            return

                        retentable = any([
                            "quota" in error_msg,
                            "rate" in error_msg,
                            "timeout" in error_msg,
                            "500" in error_msg,
                            "503" in error_msg,
                            "429" in error_msg,
                            "overloaded" in error_msg,
                        ])

                        self.logger.warning(
                            f"Erro Gemini na tentativa {attempt + 1}: {e} "
                            f"(retentável: {retentable})"
                        )

                        q.put({"error": f"Erro: {e}", "retry": retentable})

                thread = threading.Thread(target=worker)
                thread.start()
                thread.join(timeout=90.0)

                if thread.is_alive():
                    self.logger.warning(f"Thread timeout tentativa {attempt + 1}")
                    continue

                result = q.get()

                if "error" not in result:
                    return result

                # =========================================================
                # CORREÇÃO: Tratamento especial para resposta vazia
                # =========================================================
                if result.get("warning") == "empty_content":
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        self.logger.info(
                            f"Resposta vazia, aguardando {delay}s antes de retry..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        # Última tentativa, retornar mensagem padrão
                        self.logger.error("Todas as tentativas retornaram vazio")
                        return {
                            "content": "Não foi possível processar sua solicitação. Por favor, tente reformular sua pergunta.",
                            "warning": "all_attempts_empty"
                        }

                if result.get("retry") and (attempt < self.max_retries - 1):
                    delay = self.retry_delay * (2**attempt)
                    self.logger.info(
                        f"Aguardando {delay}s antes da próxima tentativa..."
                    )
                    time.sleep(delay)
                    continue

                return result

            except Exception as e:
                self.logger.error(
                    f"Erro externo tentativa {attempt + 1}: {e}", exc_info=True
                )
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    time.sleep(delay)
                    continue
                return {"error": f"Erro após {self.max_retries} tentativas: {e}"}

        return {"error": f"Falha após {self.max_retries} tentativas"}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Converte mensagens do formato OpenAI-like para formato Gemini.

        Formato OpenAI-like: [{"role": "user", "content": "..."}]
        Formato Gemini: [{"role": "user", "parts": [{"text": "..."}]}]
        """
        gemini_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            function_call = msg.get("function_call")

            if tool_calls:
                gemini_msg = {
                    "role": "model",
                    "parts": [
                        {"function_call": {"name": tc["function"]["name"], "args": json.loads(tc["function"]["arguments"])}}
                        for tc in tool_calls
                    ]
                }
            elif function_call:
                gemini_msg = {
                    "role": "user",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call["name"],
                                "response": {"content": content}
                            }
                        }
                    ]
                }
            elif role == "user":
                gemini_msg = {"role": "user", "parts": [{"text": content}]}
            elif role == "assistant" or role == "model":
                gemini_msg = {"role": "model", "parts": [{"text": content}]}
            else:
                self.logger.warning(f"Unexpected role encountered: {role}. Treating as 'user'.")
                gemini_msg = {"role": "user", "parts": [{"text": content}]}

            gemini_messages.append(gemini_msg)

        return gemini_messages

    def _convert_tools(self, tools_wrapper: Dict[str, List[Dict[str, Any]]]) -> List[FunctionDeclaration]:
        """
        Converte ferramentas do formato OpenAI-like para Gemini Tool Format.
        """
        gemini_tools = []
        function_declarations = tools_wrapper.get("function_declarations", [])

        for tool_declaration in function_declarations:
            gemini_tool = FunctionDeclaration(
                name=tool_declaration.get("name", ""),
                description=tool_declaration.get("description", ""),
                parameters=tool_declaration.get("parameters", {}),
            )
            gemini_tools.append(gemini_tool)

        return gemini_tools
