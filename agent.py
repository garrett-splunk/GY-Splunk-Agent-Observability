"""
LangGraph IT Helpdesk agent.

INSTRUMENTATION (Exercises 3 & 4):
  - Exercise 3: Attach GalileoCallback to graph.ainvoke config callbacks
  - Exercise 4: Call ensure_trace_started / finalize_trace around each query
  Reference: ~/Desktop/galileo-golden-demo/agent_frameworks/langgraph/agent.py
"""
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from helpers.llm import LLMProvider, SPAN_NAME, get_chat_model
from helpers.trace_lifecycle import ensure_trace_started, finalize_trace
from tools import TOOLS, set_galileo_logger

from galileo.handlers.langchain import GalileoCallback

try:
    from agent_control import ControlViolationError, control
    from helpers.agent_control_helpers import BLOCKED_MESSAGE

    _AGENT_CONTROL_AVAILABLE = True
except ImportError:
    _AGENT_CONTROL_AVAILABLE = False


class State(TypedDict):
    messages: Annotated[list, add_messages]


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coro).result()


class ITHelpdeskAgent:
    def __init__(
        self,
        config: Dict[str, Any],
        *,
        session_id: Optional[str] = None,
        galileo_logger=None,
        llm_provider: LLMProvider = "local",
        model_override: Optional[str] = None,
    ):
        self.config = config
        self.session_id = session_id or str(uuid.uuid4())[:10]
        self.galileo_logger = galileo_logger
        self.llm_provider = llm_provider
        self.model_override = model_override
        self.system_prompt = config.get("system_prompt", "").strip()
        self.graph = None
        self.tools = self._build_langchain_tools()

        callbacks = []
        if galileo_logger:
            callbacks.append(
                GalileoCallback(
                    galileo_logger=galileo_logger,
                    start_new_trace=False,
                    flush_on_chain_end=False,
                )
            )
        self.invoke_config = {
            "configurable": {"thread_id": self.session_id},
            "callbacks": callbacks,
        }

        if galileo_logger:
            set_galileo_logger(galileo_logger)

    def _build_langchain_tools(self) -> List[StructuredTool]:
        bound = []
        for tool_func in TOOLS:
            bound.append(
                StructuredTool.from_function(
                    func=tool_func,
                    name=tool_func.__name__,
                    description=tool_func.__doc__ or tool_func.__name__,
                )
            )
        return bound

    def _build_graph(self):
        model_cfg = self.config.get("model", {})
        if self.model_override:
            effective_model = self.model_override
        elif self.llm_provider == "hosted":
            effective_model = model_cfg.get("hosted_default_model", "gpt-4o")
        else:
            effective_model = model_cfg.get("default_model", "gemma4")
        temperature = model_cfg.get("temperature", 0.1)

        llm = get_chat_model(
            effective_model,
            temperature=temperature,
            provider=self.llm_provider,
        ).bind_tools(self.tools)

        use_agent_control = (
            _AGENT_CONTROL_AVAILABLE
            and self.config.get("galileo", {}).get("enable_agent_control")
            and self.galileo_logger is not None
        )

        if use_agent_control:

            @control(step_name=SPAN_NAME)
            async def _invoke_llm(msgs):
                return await llm.ainvoke(msgs)

            async def invoke_chatbot(state: State):
                messages = list(state["messages"])
                if self.system_prompt:
                    messages = [SystemMessage(content=self.system_prompt)] + messages
                try:
                    result = await _invoke_llm(messages)
                except ControlViolationError:
                    result = AIMessage(content=BLOCKED_MESSAGE)
                return {"messages": [result]}
        else:

            async def invoke_chatbot(state: State):
                messages = list(state["messages"])
                if self.system_prompt:
                    messages = [SystemMessage(content=self.system_prompt)] + messages
                result = await llm.ainvoke(messages)
                return {"messages": [result]}

        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", invoke_chatbot)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        return graph_builder.compile()

    async def _process_query_async(self, messages: List[Dict[str, str]]) -> str:
        if self.graph is None:
            self.graph = self._build_graph()

        langchain_messages: List[BaseMessage] = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))

        response = "No response generated"
        try:
            # INSTRUMENTATION (Exercise 4): start trace before graph.ainvoke
            ensure_trace_started(
                self.galileo_logger,
                langchain_messages,
                trace_name="Run Agent",
            )

            result = await self.graph.ainvoke(
                {"messages": langchain_messages},
                self.invoke_config,
            )
            if result["messages"]:
                last = result["messages"][-1]
                response = getattr(last, "content", str(last))
            return response
        finally:
            # INSTRUMENTATION (Exercise 4): conclude + flush trace
            if self.galileo_logger:
                finalize_trace(self.galileo_logger, response)

    def process_query(self, messages: List[Dict[str, str]]) -> str:
        return _run_async(self._process_query_async(messages))
