# LangChain Knowledge Hub

> Baseline knowledge of the LangChain ecosystem for an AI agent. Condensed from the official
> docs at **https://docs.langchain.com**. Code examples are Python; a parallel TypeScript/JavaScript
> API exists for every package (swap `/oss/python/` → `/oss/javascript/` in any link below).
>
> **Doc link convention:** every link is `https://docs.langchain.com/<path>`. Paths are given
> relative to that base (e.g. `oss/python/langchain/agents`).

---

## 1. The ecosystem at a glance

LangChain is a **platform for agent engineering**. It is several layered open-source packages plus a
commercial platform (LangSmith). Understanding the layers is the single most important thing:

| Layer | Package | Role | When to use |
|---|---|---|---|
| **Harness** | **Deep Agents** (`deepagents`) | Batteries-included agent: planning, virtual filesystem, subagents, context management | Complex, long-running, autonomous tasks (research, coding) |
| **Framework** | **LangChain** (`langchain`) | Abstractions + integrations; `create_agent` harness, models, tools, messages, middleware | Build customizable agents fast with standard building blocks |
| **Runtime** | **LangGraph** (`langgraph`) | Low-level orchestration: graphs, durable execution, persistence, streaming, HITL | Fine-grained control; mix deterministic + agentic workflows |
| **Platform** | **LangSmith** | Observability (tracing), evaluation, prompt engineering, deployment, LLM gateway | Trace/debug/eval/deploy agents built with *any* framework |

**Dependency direction:** Deep Agents → built on → LangChain → built on → LangGraph. You can use any
layer directly; you don't need to know LangGraph to use LangChain.

**Mental model — "Agent = Model + Harness":** An agent is *a model calling tools in a loop until a
task is complete*. The **harness** is everything around that loop — the prompt, the tools, and the
middleware that shapes behavior. The harness's job: *get the model the right context at the right
time.*

Key concept pages:
- Frameworks, runtimes, and harnesses: `oss/python/concepts/products`
- Providers and models: `oss/python/concepts/providers-and-models`
- Context (engineering) overview: `oss/python/concepts/context`
- Memory overview: `oss/python/concepts/memory`
- Index / landing: `index`

---

## 2. LangChain (the framework)

Docs root: `oss/python/langchain/overview` · Philosophy/history: `oss/python/langchain/philosophy`

> **v1.0 note (Oct 2025):** All legacy chains/agents were replaced by a single high-level abstraction:
> `create_agent` (built on LangGraph). Old chains live in the `langchain-classic` package. Messages
> now use a standard multimodal **content blocks** format across providers.

### 2.1 `create_agent` — the core API

```python
# pip install -qU langchain "langchain[anthropic]"
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-6",          # "provider:model" string OR a model instance
    tools=[get_weather],                 # callables, @tool objects, or dicts
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in SF?"}]}
)
print(result["messages"][-1].content_blocks)
```

Key `create_agent` parameters:
- `model` — `"provider:model"` string (e.g. `"openai:gpt-5.4"`, `"anthropic:claude-sonnet-4-6"`,
  `"google_genai:gemini-3.5-flash"`) or an initialized chat model instance.
- `tools` — list of tools (see §2.4).
- `system_prompt` — string or `SystemMessage`. For *dynamic* prompts, use middleware.
- `response_format` — schema for structured output (see §2.5).
- `middleware` — list of middleware to extend the loop (see §2.6).
- `checkpointer` — enables short-term memory / thread persistence (see §2.7).
- `store` — enables long-term memory across threads (see §2.8).
- `context_schema` — typed per-run dependency injection (see §2.9).
- `state_schema` — extend the agent's state with custom fields.
- `name` — node name when embedded as a subgraph in multi-agent systems.

Page: `oss/python/langchain/agents`

### 2.2 Invocation, threads & follow-ups

Invoke by passing a state update (`{"messages": [...]}`). To persist conversation history across
turns, configure a `checkpointer` and pass a `thread_id`:

```python
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.utils.uuid import uuid7

agent = create_agent(model="openai:gpt-5.4", tools=[], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": str(uuid7())}}

agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob."}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)  # remembers "Bob"
```

- `thread_id` scopes the conversation (history + checkpoints).
- `context` carries per-run data (user ID, keys) for tools/middleware to read.
- Both are commonly passed together. On LangSmith deployment a checkpointer is provisioned automatically.

### 2.3 Models

Page: `oss/python/langchain/models` · Concept: `oss/python/concepts/providers-and-models`

LangChain provides **one standard interface for any provider** — swap providers without rewriting
logic. Models can be used inside agents *or* standalone.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-6")   # unified factory
response = model.invoke("Explain quantum computing in one sentence.")
print(response.text)
```

- Provider-specific classes also exist: `ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`, etc.
- Each provider has its own package: `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, …
- API keys via env vars (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- Capabilities: tool calling, structured output, multimodality (images/audio/files/video), reasoning.
- Model capabilities are read from **profile data** (`langchain>=1.1`); override with `init_chat_model(..., profile={...})`.

### 2.4 Tools

Page: `oss/python/langchain/tools`

```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"
```

- The `@tool` decorator turns a function into a tool; the **docstring becomes the description** the
  model uses to decide when to call it. **Type hints are required** (they define the input schema).
- Prefer `snake_case` tool names; some providers reject spaces/special chars.
- Override name/description: `@tool("web_search", description="...")`.
- Complex inputs: pass a Pydantic model or JSON schema via `args_schema=`.
- **Server-side tools** (provider-hosted web search / code interpreter) run on the provider side.
- Access runtime inside a tool with the `ToolRuntime` parameter (see §2.9).

### 2.5 Structured output

Page: `oss/python/langchain/structured-output`

Return validated, typed data instead of free text. Set `response_format=` on `create_agent`; the
result lands in `result["structured_response"]`.

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent

class ContactInfo(BaseModel):
    name: str = Field(description="The person's name")
    email: str
    phone: str

agent = create_agent(model="gpt-5.4", response_format=ContactInfo)
result = agent.invoke({"messages": [{"role": "user", "content": "Extract: John Doe, john@x.com, 555-1234"}]})
result["structured_response"]   # ContactInfo(...)
```

Strategies (`response_format` accepts a schema type, or one of these wrappers):
- **`ProviderStrategy`** — uses provider-native structured output (OpenAI, Anthropic, Gemini, xAI). Most reliable.
- **`ToolStrategy`** — uses tool calling to coerce output (works on any tool-calling model).
- Passing a bare schema type auto-selects: provider-native if supported, else tool strategy.
- Supports Pydantic models (validated instance), dataclasses/TypedDict/JSON schema (dict).

### 2.6 Middleware — the customization primitive

Pages: overview `oss/python/langchain/middleware/overview` · built-in `oss/python/langchain/middleware/built-in` · custom `oss/python/langchain/middleware/custom`

Middleware hooks into the agent loop (before/after model calls, before/after tool calls). Each piece
handles **one concern** and composes freely. This is *the* mechanism for context engineering.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-5.4",
    tools=[...],
    middleware=[SummarizationMiddleware(...), HumanInTheLoopMiddleware(...)],
)
```

Notable built-in / ecosystem middleware:
- **Context management:** `SummarizationMiddleware` (compress history before overflow), `MemoryMiddleware`
  (load persistent instructions, e.g. `AGENTS.md`), `SkillsMiddleware` (load domain knowledge on demand).
- **Execution environment:** `FilesystemMiddleware` (virtual FS via a backend), Sandboxes, Interpreters.
- **Planning/delegation:** `TodoListMiddleware`, `SubAgentMiddleware`.
- **Fault tolerance:** `ModelRetryMiddleware`, `ToolRetryMiddleware`.
- **Guardrails:** `PIIMiddleware` (redact/mask/hash/block PII).
- **Steering:** `HumanInTheLoopMiddleware` (pause for approval).
- **Dynamic prompt:** `@dynamic_prompt` decorator returns a prompt computed from request state/context.

Middleware runs *inside* the compiled LangGraph that `create_agent` returns, so the whole agent (with
all middleware) can be dropped into a larger `StateGraph` as a node/subgraph.

### 2.7 Short-term memory (threads)

Page: `oss/python/langchain/short-term-memory`

Thread-scoped conversation history. Add a **checkpointer**; state is persisted per `thread_id` and
resumable. Use `InMemorySaver` locally; DB-backed checkpointers (Postgres) in production.

### 2.8 Long-term memory (store)

Page: `oss/python/langchain/long-term-memory`

Persists across threads/sessions. Built on **LangGraph stores** — JSON documents organized by
`namespace` + `key`.

```python
from langgraph.store.memory import InMemoryStore
from langchain.agents import create_agent

store = InMemoryStore()                       # use PostgresStore in production
agent = create_agent("claude-sonnet-4-6", tools=[], store=store)
```

Memory types (from cognitive science, see `oss/python/concepts/memory`):
- **Semantic** — facts about the user (profile doc or collection of docs).
- **Episodic** — past experiences (often few-shot examples).
- **Procedural** — rules/instructions (system prompt; can self-refine via reflection).
Write strategies: "hot path" (during the run) vs "background" (async task).

### 2.9 Runtime & context (dependency injection)

Page: `oss/python/langchain/runtime` · Concept: `oss/python/concepts/context`

`create_agent` runs on LangGraph's **Runtime**, which exposes: `context` (static per-run config),
`store` (long-term memory), `stream_writer`, `execution_info` (thread/run/attempt IDs), `server_info`.

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent

@dataclass
class Context:
    user_id: str

@tool
def fetch_prefs(runtime: ToolRuntime[Context]) -> str:
    """Fetch the user's preferences."""
    user_id = runtime.context.user_id
    if runtime.store and (mem := runtime.store.get(("users",), user_id)):
        return mem.value["preferences"]
    return "default"

agent = create_agent("gpt-5-nano", tools=[fetch_prefs], context_schema=Context)
agent.invoke({"messages": [...]}, context=Context(user_id="user-123"))
```

Three kinds of context (the heart of **context engineering** — providing the right info/tools in the
right format so the LLM can succeed):
| Type | a.k.a. | Scope | Examples |
|---|---|---|---|
| **Runtime context** | static config | per-conversation | user ID, API keys, DB connections, permissions |
| **State** | short-term memory | per-conversation | messages, uploaded files, tool results |
| **Store** | long-term memory | cross-conversation | preferences, extracted insights, memories |

### 2.10 Streaming

Page: `oss/python/langchain/streaming` · Event streaming: `oss/python/langchain/event-streaming`

```python
for chunk in agent.stream({"messages": [...]}, stream_mode="updates", version="v2"):
    ...
```

Stream modes: **`updates`** (state after each step), **`messages`** (LLM token + metadata tuples),
**`custom`** (user-emitted data via the stream writer). v1.3+ introduces typed **event streaming**
(separate iterators per projection: messages, values, tool calls, subgraphs).

### 2.11 Retrieval & RAG

Pages: retrieval `oss/python/langchain/retrieval` · RAG tutorial `oss/python/langchain/rag` · component architecture `oss/python/langchain/component-architecture`

Retrieval fixes LLM limits (finite context, frozen knowledge) by fetching external knowledge at query
time. Pipeline: **Sources → Document Loaders → split into chunks → embeddings → Vector Store →
Retriever → LLM uses retrieved context → Answer**.

Building blocks: **Document loaders**, **Text splitters** (e.g. `RecursiveCharacterTextSplitter`),
**Embedding models**, **Vector stores**, **Retrievers**.

RAG architectures:
| Architecture | How | Best for |
|---|---|---|
| **2-Step RAG** | Always retrieve, then generate (1 LLM call) | FAQs, doc bots; predictable/fast |
| **Agentic RAG** | Agent decides when/how to retrieve (search as a tool) | Research assistants; flexible |
| **Hybrid** | Combines both + validation steps | Domain Q&A with quality checks |

### 2.12 Human-in-the-loop (HITL)

Page: `oss/python/langchain/human-in-the-loop`

`HumanInTheLoopMiddleware` pauses the agent before sensitive tool calls (requires a checkpointer).
Four decision types: **approve**, **edit** (modify args), **reject** (with feedback), **respond**
(human's reply becomes the tool result).

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware
HumanInTheLoopMiddleware(interrupt_on={
    "write_file": True,                                  # all decisions allowed
    "execute_sql": {"allowed_decisions": ["approve", "reject"]},
    "read_data": False,                                  # auto-approve
})
```

### 2.13 Guardrails

Page: `oss/python/langchain/guardrails`

Safety/compliance via middleware. **Deterministic** (regex/keyword/rules — fast, predictable) vs
**model-based** (LLM/classifier — catches nuance, slower). Built-in `PIIMiddleware` strategies:
`redact`, `mask`, `hash`, `block`; apply to input and/or output.

### 2.14 Multi-agent systems

Pages: index `oss/python/langchain/multi-agent/index` · subagents/handoffs/skills/router/custom-workflow under `oss/python/langchain/multi-agent/`

Use multi-agent for: context management, distributed development, parallelization. **Context
engineering — deciding what each agent sees — is the central concern.** For batteries-included
multi-agent, prefer **Deep Agents**.

| Pattern | How it works | Strength |
|---|---|---|
| **Subagents** | Main agent calls subagents as tools; all routing through main agent | Strong context isolation, parallelism, multi-hop |
| **Handoffs** | Tool calls update state → switch active agent | Stateful, efficient on repeat turns |
| **Skills** | Single agent loads specialized prompts/knowledge on demand | Stays in control; efficient for repeats |
| **Router** | A classifier routes input to specialist agents; results synthesized | Parallel, good for multi-domain |
| **Custom workflow** | Bespoke `StateGraph` mixing deterministic + agentic nodes | Maximum control |

Subagents are stateless (repeat the full flow, ~consistent cost). Handoffs/Skills are stateful (save
40–50% of calls on repeat requests). For multi-domain parallel work, Subagents/Router are most efficient.

### 2.15 MCP (Model Context Protocol)

Page: `oss/python/langchain/mcp` · Library: `langchain-mcp-adapters`

Use tools hosted on MCP servers. `MultiServerMCPClient` is stateless by default (fresh session per call).

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient({
    "math":    {"transport": "stdio", "command": "python", "args": ["/path/math_server.py"]},
    "weather": {"transport": "http",  "url": "http://localhost:8000/mcp"},
})
tools = await client.get_tools()
agent = create_agent("claude-sonnet-4-6", tools)
```

Build custom MCP servers with **FastMCP** (`@mcp.tool()`).

### 2.16 Messages

Page: `oss/python/langchain/messages`

Messages are the fundamental unit of model context: **Role + Content + Metadata**. Standard types:
`SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`. Accepts message objects, dicts (OpenAI
format), or a bare string (shorthand for one `HumanMessage`). v1 supports multimodal **content blocks**
(`.content_blocks`) standardized across providers (text, reasoning, citations, images, etc.).

### 2.17 Other framework topics
- Install: `oss/python/langchain/install` · Quickstart: `oss/python/langchain/quickstart`
- Component architecture: `oss/python/langchain/component-architecture`
- Context engineering (deep dive): `oss/python/langchain/context-engineering`
- Knowledge base / SQL agent / voice agent: `oss/python/langchain/knowledge-base`, `.../sql-agent`, `.../voice-agent`
- Observability (in-framework): `oss/python/langchain/observability`
- Deploy / Studio / UI: `oss/python/langchain/deploy`, `.../studio`, `.../ui`
- Common errors: `oss/python/common-errors` · Get help: `oss/python/langchain/get-help`
- Migration to v1: `oss/python/migrate/langchain-v1` · Changelog: `oss/python/releases/langchain-v1`

---

## 3. LangGraph (the runtime / orchestration layer)

Docs root: `oss/python/langgraph/overview` · "Thinking in LangGraph": `oss/python/langgraph/thinking-in-langgraph`

Low-level framework for **long-running, stateful agents**. Provides: durable execution, streaming,
human-in-the-loop, persistence, comprehensive memory. Inspired by Google **Pregel** (message-passing,
"super-steps"). Usable standalone (no LangChain required). Trusted by Klarna, Uber, J.P. Morgan, etc.

### 3.1 Graph API

Page: `oss/python/langgraph/graph-api` · Use guide: `oss/python/langgraph/use-graph-api`

Three components:
- **State** — shared data structure (schema + reducers). Usually a `TypedDict`; can be dataclass or
  Pydantic model. Reducers define how node updates merge (e.g. `Annotated[list, add]` appends).
- **Nodes** — functions `(state) -> state_update`. Contain LLM calls or plain code.
- **Edges** — decide the next node (fixed or conditional). "Nodes do the work; edges say what's next."

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()                                   # validates structure; attach checkpointer here
graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
```

You **must compile** before use. Supports multiple schemas (private internal channels, distinct
input/output schemas). Note: the higher-level `create_agent` does **not** support Pydantic state schemas.

### 3.2 Persistence & checkpoints

Page: `oss/python/langgraph/persistence`

Compile with a **checkpointer** to snapshot state at every super-step, organized into **threads**
(keyed by `thread_id`). Enables: human-in-the-loop, conversational memory, **time travel**
(replay/fork from any checkpoint), **fault tolerance** (resume from last good step; pending writes
avoid re-running succeeded nodes). A **checkpoint** is a `StateSnapshot` at a super-step boundary.
Checkpoint namespace (`checkpoint_ns`) distinguishes parent graph (`""`) from subgraphs.

### 3.3 Interrupts (dynamic HITL)

Page: `oss/python/langgraph/interrupts`

`interrupt(value)` pauses execution anywhere in a node (requires checkpointer + `thread_id`), surfaces
a JSON-serializable payload to the caller, and waits indefinitely. Resume with `Command(resume=value)`
— that value becomes `interrupt()`'s return. The node **re-runs from its start** on resume (code
before `interrupt` runs again).

```python
from langgraph.types import interrupt, Command

def approval_node(state):
    approved = interrupt("Do you approve?")    # pauses here
    return {"approved": approved}

# resume:  graph.invoke(Command(resume=True), config={"configurable": {"thread_id": "1"}})
```

Prefer event streaming (`graph.stream_events(..., version="v3")`): interrupts appear on
`stream.interrupts`, `stream.interrupted`; final state via `stream.output`. Only `Command(resume=...)`
is valid as graph *input*; `update`/`goto`/`graph` are for returning *from* nodes.

### 3.4 APIs & other topics
- **Graph API vs Functional API:** `oss/python/langgraph/choosing-apis`. Functional API (`@entrypoint`,
  `@task`) for imperative style: `oss/python/langgraph/functional-api`, `.../use-functional-api`.
- **Workflows vs agents:** `oss/python/langgraph/workflows-agents` (prompt chaining, routing,
  parallelization, orchestrator-worker, evaluator-optimizer patterns).
- **Subgraphs:** `oss/python/langgraph/use-subgraphs` · **Time travel:** `.../use-time-travel`
- **Memory:** `oss/python/langgraph/add-memory` · **Streaming:** `.../streaming`, `.../event-streaming`
- **Pregel internals:** `oss/python/langgraph/pregel` · **Fault tolerance:** `.../fault-tolerance`
- **Agentic RAG:** `oss/python/langgraph/agentic-rag` · **SQL agent:** `.../sql-agent`
- **Deploy / local server / Studio:** `.../deploy`, `.../local-server`, `.../studio`
- Install `oss/python/langgraph/install` · Quickstart `.../quickstart` · Migrate `oss/python/migrate/langgraph-v1`

---

## 4. Deep Agents (the harness)

Docs root: `oss/python/deepagents/overview` · Quickstart: `oss/python/deepagents/quickstart` · Package: `deepagents`

Batteries-included agent harness on top of LangChain/LangGraph for **complex, long-running,
autonomous tasks** (research, coding). Same tool-calling loop, but with built-in capabilities.

```python
# pip install -qU deepagents
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf"}]})
```

Built-in capabilities:
- **Planning** — a to-do list to track multi-step work.
- **Virtual filesystem** — read/write files across turns; pluggable **backends** (in-memory `StateBackend`,
  disk, LangGraph store, sandboxes).
- **Subagents** — spawn general or specialized workers in isolated context windows (parallel work).
- **Context management** — auto-summarize history, evict/offload large tool results.
- **Memory, skills, MCP, HITL, sandboxes/interpreters.**

Key topic pages (under `oss/python/deepagents/`): `customization`, `subagents`, `skills`, `memory`,
`backends`, `sandboxes`, `interpreters`, `human-in-the-loop`, `mcp`, `context-engineering`,
`deep-research`, `going-to-production`, `harness`, `models`, `permissions`, `streaming`, `a2a`, `acp`,
`comparison` (vs Claude Agent SDK).

Deep Agents vs LangChain: use Deep Agents for autonomous multi-step tasks with predefined tools; use
LangChain (`create_agent`) for full control over a custom architecture.

---

## 5. LangSmith (the platform)

Docs root: `langsmith/home` · Pricing: `langsmith/pricing-plans`. Compliance: HIPAA, SOC 2 Type 2, GDPR.

Platform to **trace, evaluate, iterate on prompts, and deploy** agents from *any* framework. Enable
tracing by setting `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY`.

### 5.1 Observability (tracing)

Concept: `langsmith/observability-concepts` · Quickstart: `langsmith/observability-quickstart`

Data model: **Project** → **Traces** → **Runs** (spans). Multi-turn conversations link traces into a
**Thread** (via metadata key `session_id`/`thread_id`/`conversation_id`). Attach **feedback** (scores),
**tags**, and **metadata** to runs. Max 25,000 runs/trace. SaaS retention: 400 days.

Two ways to send traces:
- **Integrations / auto-instrumentation** — automatic for LangChain, LangGraph, OpenAI, Anthropic,
  CrewAI, and many more (see `langsmith/integrations` and `trace-with-*` pages).
- **Manual instrumentation** — `@traceable` decorator, `trace` context manager, or low-level `RunTree`.

Related: `langsmith/dashboards`, `langsmith/alerts`, `langsmith/insights`, `langsmith/cost-tracking`,
`langsmith/threads`. **Engine** (beta) auto-detects recurring issues in traces and proposes PR fixes
(`langsmith/engine`).

### 5.2 Evaluation

Concept: `langsmith/evaluation-concepts` · Quickstart: `langsmith/evaluation-quickstart`

Measure quality of non-deterministic LLM outputs. Start with 5–10 hand-curated "good" examples.
- **Offline evals** — pre-deployment, against **datasets** with reference outputs (benchmarking,
  regression testing, unit testing, backtesting).
- **Online evals** — production monitoring on live runs/threads, no reference outputs (real-time
  quality, anomaly detection).
- **Evaluators:** LLM-as-judge (`langsmith/llm-as-judge`), code evaluators, composite, pairwise,
  summary evaluators (aggregate metrics like F1 over a whole experiment). See `langsmith/evaluators`,
  `langsmith/evaluation-types`, `langsmith/openevals`.
- Manage datasets: `langsmith/manage-datasets`. Tutorials: evaluate RAG/chatbot/complex agent under
  `langsmith/evaluate-*`.

### 5.3 Prompt engineering
Concept `langsmith/prompt-engineering-concepts` · Quickstart `langsmith/prompt-engineering-quickstart`.
Version-controlled prompts, the Playground, optimization, collaboration. Manage programmatically:
`langsmith/manage-prompts`. **Polly** AI assistant: `langsmith/polly`.

### 5.4 Deployment (Agent Server)
Overview `langsmith/deployment` · Quickstart `langsmith/deployment-quickstart`. Deploy long-running
stateful agents one-click; checkpointing/persistence handled automatically. Options: cloud
(`langsmith/cloud`), hybrid (`langsmith/hybrid`), self-hosted (`langsmith/self-hosted`). **Studio**
visual prototyping: `langsmith/studio`. **Assistants:** `langsmith/assistants`. Concepts:
control plane / data plane (`langsmith/control-plane`, `langsmith/data-plane`).

### 5.5 LLM Gateway (private beta)
`langsmith/llm-gateway` — proxy LLM calls to enforce spend limits/policies (`langsmith/llm-gateway-spend-policies`),
redact sensitive data (`langsmith/llm-gateway-redaction`), centrally manage provider credentials.

### 5.6 SDKs & APIs
Python `langsmith/smith-python-sdk` · JS/TS `langsmith/smith-js-ts-sdk` · Go `langsmith/smith-go-sdk`
· Java `langsmith/smith-java-sdk`. CLI `langsmith/cli`. Server API ref `langsmith/server-api-ref`.
MCP server `langsmith/langsmith-mcp-server`. LangGraph SDKs: `langsmith/langgraph-python-sdk`,
`langsmith/langgraph-js-ts-sdk`.

### 5.7 LangSmith Fleet
No-code agent builder — start from a template, connect accounts, automate routine work. See
`api-reference/` (fleet sub-area).

---

## 6. Integrations

Overview: `oss/python/integrations/providers/overview` · All providers: `.../all_providers`

700+ integrations, split into per-provider packages. Categories (browse under
`oss/python/integrations/<category>/`):
- **chat** (chat models) · **llms** (text LLMs) · **embeddings** · **vectorstores** · **retrievers**
- **document_loaders** · **document_transformers** · **splitters** · **tools** · **stores**
- **middleware** · **sandboxes** · **checkpointers** · **llm_caching**

Major providers with dedicated pages: `anthropic`, `openai`, `google`, `aws`, `microsoft`, `groq`,
`fireworks`, `huggingface`, `nvidia`, `ollama` (e.g. `oss/python/integrations/providers/anthropic`).

---

## 7. API reference

Overview: `oss/python/reference/overview`
- LangChain Python: `oss/python/reference/langchain-python`
- LangGraph Python: `oss/python/reference/langgraph-python`
- Deep Agents Python: `oss/python/reference/deepagents-python`
- Integrations: `oss/python/reference/integrations-python`
(TypeScript equivalents under `oss/javascript/reference/`.)

---

## 8. Quick decision guide (for an agent choosing tools)

- **Single LLM call / simple chat** → a chat model via `init_chat_model` (no agent needed).
- **Tool-calling agent, want it fast & customizable** → `langchain.create_agent` + middleware.
- **Autonomous, long-running, multi-step (research/coding)** → `deepagents.create_deep_agent`.
- **Need exact control over branching / deterministic + agentic mix** → LangGraph `StateGraph`.
- **Conversation memory across turns** → add a `checkpointer` + `thread_id` (short-term);
  add a `store` for cross-session (long-term).
- **Need human approval before risky actions** → `HumanInTheLoopMiddleware` (LangChain) or
  `interrupt()` (LangGraph) — both require a checkpointer.
- **Structured/typed result** → `response_format=` (LangChain) or `.with_structured_output()` on a model.
- **External tools over a protocol** → `langchain-mcp-adapters` + `MultiServerMCPClient`.
- **Trace / debug / evaluate / deploy** → LangSmith (`LANGSMITH_TRACING=true`).

---

## 9. Key naming & gotchas
- **v1.0 (Oct 2025):** legacy chains/agents removed from `langchain`; one abstraction = `create_agent`.
  Legacy code → `langchain-classic`. Messages use standard **content blocks**.
- `create_agent` (LangChain) ≈ the prebuilt ReAct agent that used to live in LangGraph.
- A **checkpointer** powers thread/short-term memory + HITL + time travel; a **store** powers
  long-term cross-thread memory. Different objects, different scopes.
- `thread_id` (in `config["configurable"]`) ≠ `context` (per-run dependency injection). Often passed together.
- "Runtime context" ≠ "LLM context window." Runtime context = dependency injection for your code.
- LangGraph graphs **must be compiled** before invocation.
- On resume after `interrupt()`, the node re-runs from its beginning.
- Python paths shown here map 1:1 to JS/TS: replace `oss/python/` with `oss/javascript/`.
```
