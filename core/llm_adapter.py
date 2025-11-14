from typing import List, Dict, Any, Optional
import logging
import threading
import time
from queue import Queue
from core.llm_base import BaseLLMAdapter
from core.config.config import Config
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

class OpenAILLMAdapter(BaseLLMAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(
            api_key=Config().OPENAI_API_KEY,
            timeout=60.0,  # Aumentado para 60 segundos
        )
        self.max_retries = 3  # Máximo de tentativas
        self.retry_delay = 2  # Delay inicial entre tentativas (segundos)

    def get_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Obtém completion da API OpenAI com retry automático.
        
        Args:
            messages: Lista de mensagens
            tools: Lista opcional de ferramentas
            
        Returns:
            Dicionário com resultado ou erro
        """
        for attempt in range(self.max_retries):
            try:
                q = Queue()

                def worker():
                    try:
                        # Preparar argumentos da API
                        api_args = {
                            "model": Config().LLM_MODEL_NAME,
                            "messages": messages,
                            "temperature": 0,
                        }
                        if tools:
                            api_args["tools"] = tools
                            api_args["tool_choice"] = "auto"

                        self.logger.info(
                            f"Chamada OpenAI (tentativa {attempt + 1}/"
                            f"{self.max_retries})"
                        )
                        response = self.client.chat.completions.create(
                            **api_args
                        )
                        self.logger.info("Chamada OpenAI concluída.")

                        # Extrair conteúdo
                        message_content = (
                            response.choices[0].message.content
                        )
                        tool_calls = (
                            response.choices[0].message.tool_calls
                        )

                        result = {"content": message_content}
                        if tool_calls:
                            result["tool_calls"] = tool_calls

                        q.put(result)

                    except APITimeoutError as e:
                        self.logger.warning(
                            f"Timeout na tentativa {attempt + 1}: {e}"
                        )
                        q.put({
                            "error": f"Timeout: {e}",
                            "retry": True
                        })
                    except APIConnectionError as e:
                        self.logger.warning(
                            f"Erro conexão na tentativa {attempt + 1}: {e}"
                        )
                        q.put({
                            "error": f"Conexão: {e}",
                            "retry": True
                        })
                    except RateLimitError as e:
                        self.logger.warning(
                            f"Rate limit na tentativa {attempt + 1}: {e}"
                        )
                        q.put({
                            "error": f"Rate limit: {e}",
                            "retry": True
                        })
                    except Exception as e:
                        self.logger.error(
                            f"Erro inesperado tentativa {attempt + 1}: {e}",
                            exc_info=True
                        )
                        q.put({"error": f"Erro: {e}"})

                thread = threading.Thread(target=worker)
                thread.start()
                thread.join(timeout=90.0)

                if thread.is_alive():
                    self.logger.warning(
                        f"Thread timeout tentativa {attempt + 1}"
                    )
                    # Continuar para próxima tentativa
                    continue

                result = q.get()

                # Se sucesso, retornar
                if "error" not in result:
                    return result

                # Se erro retentável, continuar
                if result.get("retry") and (
                    attempt < self.max_retries - 1
                ):
                    delay = self.retry_delay * (2 ** attempt)
                    self.logger.info(
                        f"Aguardando {delay}s antes da próxima "
                        f"tentativa..."
                    )
                    time.sleep(delay)
                    continue

                # Se não retentável, retornar erro
                return result

            except Exception as e:
                self.logger.error(
                    f"Erro externo tentativa {attempt + 1}: {e}",
                    exc_info=True
                )
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                return {"error": f"Erro após {self.max_retries} "
                        f"tentativas: {e}"}

        return {
            "error": f"Falha após {self.max_retries} tentativas"
        }
