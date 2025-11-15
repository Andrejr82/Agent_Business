# core/llm_langchain_adapter.py
from typing import Any, List, Optional
import json

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


class CustomLangChainLLM(BaseChatModel):
    llm_adapter: BaseLLMAdapter
    tools: Optional[List[Any]] = None # Adicionado para permitir o campo 'tools'

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
        """Bind tools to the model.

        Args:
            tools: A list of tools to bind to the model.
            kwargs: Additional keyword arguments.

        Returns:
            A new instance of the model with the tools bound.
        """
        # Create a new instance of the model with the tools bound
        # This is a simplified implementation. In a real scenario, you might
        # want to create a new runnable that wraps the model and the tools.
        new_instance = self.__class__(llm_adapter=self.llm_adapter, **kwargs)
        new_instance.tools = tools  # Store tools for _generate to access
        return new_instance

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Convert LangChain messages to a generic dictionary format
        # that GeminiLLMAdapter can understand (similar to OpenAI-like format)
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
                            "role": "assistant",
                            "content": msg.content,
                            "tool_calls": processed_tool_calls,
                        }
                    )
                else:
                    generic_messages.append(
                        {"role": "assistant", "content": msg.content}
                    )
            elif isinstance(msg, SystemMessage):
                generic_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, FunctionMessage):
                generic_messages.append(
                    {"role": "function", "name": msg.name, "content": msg.content}
                )
            elif isinstance(msg, ToolMessage):
                tool_message_to_send = {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": str(msg.content),
                }
                generic_messages.append(tool_message_to_send)
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")

        # Check if tools were bound via bind_tools or passed directly in kwargs
        tools_to_pass = getattr(self, 'tools', None) or kwargs.get("tools")
        if tools_to_pass:
            # Convert LangChain tools to a generic dictionary format
            generic_tools = []
            for tool in tools_to_pass:
                if hasattr(tool, 'json_schema'):
                    generic_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.json_schema,
                        }
                    })
                else:
                    # Fallback for other tool types if necessary
                    generic_tools.append(tool)
            tools_to_pass = generic_tools
        else:
            tools_to_pass = None


        llm_response = self.llm_adapter.get_completion(
            messages=generic_messages, tools=tools_to_pass
        )

        if "error" in llm_response:
            raise Exception(f"LLM Adapter Error: {llm_response['error']}")

        content = llm_response.get("content") or ""
        tool_calls_data = llm_response.get("tool_calls")

        lc_tool_calls = []
        if tool_calls_data:
            for tc_data in tool_calls_data:
                try:
                    # tc_data is already a dictionary from GeminiLLMAdapter
                    args = json.loads(tc_data["function"]["arguments"])
                except (json.JSONDecodeError, TypeError):
                    args = {
                        "error": "Argumentos em formato JSON inválido",
                        "received": tc_data["function"]["arguments"],
                    }

                lc_tool_calls.append(
                    ToolCall(name=tc_data["function"]["name"], args=args, id=tc_data["id"])
                )

        ai_message = AIMessage(content=content, tool_calls=lc_tool_calls)

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
        chat_result = self._generate(messages, stop, run_manager, **kwargs)
        generation = chat_result.generations[0]
        ai_message = generation.message

        message_chunk = AIMessageChunk(
            content=ai_message.content, tool_calls=ai_message.tool_calls
        )

        yield ChatGenerationChunk(message=message_chunk)
