# Hi, I'm quifox

🤖 Into **AI agents, LLM applications, agentic coding, MCP, RAG, and the ecosystem around them**.  
⚡ I enjoy **vibe coding** — fast iteration with AI, while still caring about understanding behavior, testing changes, and keeping systems simple.  
🔧 Backend-minded. I like turning unclear problems into **reproducible bugs and small, verifiable fixes**.

[![AI Agents](https://img.shields.io/badge/-AI_Agents-8B5CF6?style=flat-square)](https://github.com/topics/ai-agents)
[![MCP](https://img.shields.io/badge/-MCP-111111?style=flat-square)](https://modelcontextprotocol.io/)
[![RAG](https://img.shields.io/badge/-RAG-0A7EA4?style=flat-square)](https://github.com/topics/retrieval-augmented-generation)
[![Vibe Coding](https://img.shields.io/badge/-Vibe_Coding-FF6B9D?style=flat-square)](https://github.com/topics/ai-coding)
[![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![C#](https://img.shields.io/badge/-C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![.NET](https://img.shields.io/badge/-.NET-512BD4?style=flat-square&logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

I spend most of my time exploring how AI changes the way software is built: coding agents, tool use, context engineering, multi-agent workflows, retrieval, evaluation, and the infrastructure around them.

I also care about the less flashy parts — backend reliability, concurrency, caching, data consistency, search quality, and debugging things until the behavior actually makes sense.

### Things I like

- agentic coding and developer tools
- LLM applications, MCP, tool use, and RAG
- TypeScript and .NET
- CLI / TUI tooling and automation
- backend systems and distributed-system problems
- open-source debugging and small focused fixes

> **Simple systems. Explicit behavior. Reproducible results.**

### Featured Project

#### 🧩 [Agent Core](https://github.com/quifox/agent-core) · Core + Plugins → Your Application

An experimental TypeScript agent framework built around a minimal execution core and explicit plugins. Exploring how sessions, interruption, recovery, and peer-agent collaboration can be composed through lifecycle hooks.

[Repository](https://github.com/quifox/agent-core) · [Architecture](https://github.com/quifox/agent-core/blob/main/docs/guides/architecture.md) · [▶ Showcase](https://github.com/quifox/agent-core/blob/main/docs/media/agent-core-demo.mp4)

---

### Open Source Contributions

<!-- OSS-CONTRIBUTIONS:START -->
#### [`infiniflow/ragflow`](https://github.com/infiniflow/ragflow) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/infiniflow/ragflow?style=flat-square&logo=github&label=stars)](https://github.com/infiniflow/ragflow/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-1-8B5CF6?style=flat-square)

- [#20546](https://github.com/infiniflow/ragflow/pull/20546) — fix(elasticsearch): propagate search failures with index context

#### [`bytedance/deer-flow`](https://github.com/bytedance/deer-flow) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/bytedance/deer-flow?style=flat-square&logo=github&label=stars)](https://github.com/bytedance/deer-flow/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-4-8B5CF6?style=flat-square)

- [#6292](https://github.com/bytedance/deer-flow/pull/6292) — fix(acp): apply invocation timeout to initialization and session creation
- [#6272](https://github.com/bytedance/deer-flow/pull/6272) — fix(channels): handle streamed run errors before dedupe cleanup
- [#6218](https://github.com/bytedance/deer-flow/pull/6218) — fix: include completed child usage in lead budget checks
- [#6217](https://github.com/bytedance/deer-flow/pull/6217) — fix: propagate current run failures from wait endpoints

#### [`agentscope-ai/agentscope`](https://github.com/agentscope-ai/agentscope) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/agentscope-ai/agentscope?style=flat-square&logo=github&label=stars)](https://github.com/agentscope-ai/agentscope/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-3-8B5CF6?style=flat-square)

- [#3103](https://github.com/agentscope-ai/agentscope/pull/3103) — fix(scheduler): notify owner after deleting schedules
- [#3098](https://github.com/agentscope-ai/agentscope/pull/3098) — fix(workspace): clean up failed Docker initialization
- [#3090](https://github.com/agentscope-ai/agentscope/pull/3090) — fix(tool): omit injected state from inferred function schemas

#### [`microsoft/agent-framework`](https://github.com/microsoft/agent-framework) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/microsoft/agent-framework?style=flat-square&logo=github&label=stars)](https://github.com/microsoft/agent-framework/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-12-8B5CF6?style=flat-square)

- [#9001](https://github.com/microsoft/agent-framework/pull/9001) — Python: Isolate the mixed middleware warning assertion
- [#8997](https://github.com/microsoft/agent-framework/pull/8997) — Python: Preserve streamed logprobs across empty chunks
- [#8933](https://github.com/microsoft/agent-framework/pull/8933) — .NET: Synchronize background task metadata and defer publication until session creation
- [#8932](https://github.com/microsoft/agent-framework/pull/8932) — .NET: Skip empty Foundry memory context messages
- [#8931](https://github.com/microsoft/agent-framework/pull/8931) — .NET: Preserve atomic cache creation across factory failures
- [#8885](https://github.com/microsoft/agent-framework/pull/8885) — .NET: Publish synthesized terminal responses with their events
- [#8877](https://github.com/microsoft/agent-framework/pull/8877) — .NET: Preserve A2A run errors when session save fails
- [#8844](https://github.com/microsoft/agent-framework/pull/8844) — Python: support ChatKit generated image conversion
- [#8843](https://github.com/microsoft/agent-framework/pull/8843) — Python: support ChatKit structured input conversion
- [#8813](https://github.com/microsoft/agent-framework/pull/8813) — .NET: Propagate ChatHistoryMemoryProvider caller cancellation
- [#8812](https://github.com/microsoft/agent-framework/pull/8812) — .NET: Dispose AI context streaming enumerators on early exit
- [#8796](https://github.com/microsoft/agent-framework/pull/8796) — .NET: Propagate TextSearchProvider caller cancellation

#### [`mcp-use/mcp-use`](https://github.com/mcp-use/mcp-use) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/mcp-use/mcp-use?style=flat-square&logo=github&label=stars)](https://github.com/mcp-use/mcp-use/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-1-8B5CF6?style=flat-square)

- [#2687](https://github.com/mcp-use/mcp-use/pull/2687) — fix(cli): reject non-GitHub origins during deploy

#### [`nicobailon/pi-subagents`](https://github.com/nicobailon/pi-subagents) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/nicobailon/pi-subagents?style=flat-square&logo=github&label=stars)](https://github.com/nicobailon/pi-subagents/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-13-8B5CF6?style=flat-square)

- [#2675](https://github.com/nicobailon/pi-subagents/pull/2675) — fix: preserve schedule owner state after lock contention
- [#2656](https://github.com/nicobailon/pi-subagents/pull/2656) — feat: support daily and weekly zoned schedules
- [#2655](https://github.com/nicobailon/pi-subagents/pull/2655) — feat: apply reviewed worktree cleanup plans
- [#2627](https://github.com/nicobailon/pi-subagents/pull/2627) — fix(settings): save builtin agent overrides atomically
- [#2619](https://github.com/nicobailon/pi-subagents/pull/2619) — fix(profiles): validate machine overrides before applying settings
- [#2618](https://github.com/nicobailon/pi-subagents/pull/2618) — fix(missions): project global list summaries from authoritative records
- [#2616](https://github.com/nicobailon/pi-subagents/pull/2616) — feat: attach scheduled workflows to existing missions
- [#2606](https://github.com/nicobailon/pi-subagents/pull/2606) — fix: reconcile Linux zombie runners in the same PID namespace
- [#2605](https://github.com/nicobailon/pi-subagents/pull/2605) — fix: deliver goal notices after auto-drain failures
- [#2604](https://github.com/nicobailon/pi-subagents/pull/2604) — fix: isolate goal continuation notice errors per mission
- [#2528](https://github.com/nicobailon/pi-subagents/pull/2528) — test: run tool activation smoke in CI
- [#2527](https://github.com/nicobailon/pi-subagents/pull/2527) — fix: support older Git diff prefix options
- [#2517](https://github.com/nicobailon/pi-subagents/pull/2517) — fix: reject oversized run timeouts

#### [`bowenliang123/dsh-context`](https://github.com/bowenliang123/dsh-context) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/bowenliang123/dsh-context?style=flat-square&logo=github&label=stars)](https://github.com/bowenliang123/dsh-context/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-2-8B5CF6?style=flat-square)

- [#107](https://github.com/bowenliang123/dsh-context/pull/107) — fix(host): fold V4 tool-registry developer messages into the timeline
- [#106](https://github.com/bowenliang123/dsh-context/pull/106) — fix(client): ignore stale detail reads after refold

#### [`nicobailon/pi-mcp-adapter`](https://github.com/nicobailon/pi-mcp-adapter) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/nicobailon/pi-mcp-adapter?style=flat-square&logo=github&label=stars)](https://github.com/nicobailon/pi-mcp-adapter/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-8-8B5CF6?style=flat-square)

- [#743](https://github.com/nicobailon/pi-mcp-adapter/pull/743) — fix(cache): reject private metadata across sessions
- [#742](https://github.com/nicobailon/pi-mcp-adapter/pull/742) — fix: retry failed list_changed metadata publication
- [#733](https://github.com/nicobailon/pi-mcp-adapter/pull/733) — feat: autocomplete MCP prompt argument names
- [#698](https://github.com/nicobailon/pi-mcp-adapter/pull/698) — fix(jev): keep fallback search within allowed servers
- [#697](https://github.com/nicobailon/pi-mcp-adapter/pull/697) — fix(config): read UTF-8 BOM-prefixed config files
- [#693](https://github.com/nicobailon/pi-mcp-adapter/pull/693) — fix(config): preserve malformed config files on write
- [#683](https://github.com/nicobailon/pi-mcp-adapter/pull/683) → [#687](https://github.com/nicobailon/pi-mcp-adapter/pull/687) — fix(cache): invalidate stdio metadata on env mode changes
- [#678](https://github.com/nicobailon/pi-mcp-adapter/pull/678) → [#686](https://github.com/nicobailon/pi-mcp-adapter/pull/686) — fix(search): dedupe repeated query tokens

#### [`ranxianglei/billion-context`](https://github.com/ranxianglei/billion-context) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/ranxianglei/billion-context?style=flat-square&logo=github&label=stars)](https://github.com/ranxianglei/billion-context/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-2-8B5CF6?style=flat-square)

- [#1534](https://github.com/ranxianglei/billion-context/pull/1534) — fix(persist): retry dirty content stores on graceful flush
- [#1514](https://github.com/ranxianglei/billion-context/pull/1514) — fix(session): report native compaction ref count correctly

#### [`HsiangNianian/dsh-auto-continue`](https://github.com/HsiangNianian/dsh-auto-continue) &nbsp;&nbsp; [![Stars](https://img.shields.io/github/stars/HsiangNianian/dsh-auto-continue?style=flat-square&logo=github&label=stars)](https://github.com/HsiangNianian/dsh-auto-continue/stargazers) &nbsp; ![Contributions](https://img.shields.io/badge/contributions-3-8B5CF6?style=flat-square)

- [#55](https://github.com/HsiangNianian/dsh-auto-continue/pull/55) — fix(host): allow manual resume through active pauses
- [#54](https://github.com/HsiangNianian/dsh-auto-continue/pull/54) — fix(client): preserve newer settings drafts during saves
- [#53](https://github.com/HsiangNianian/dsh-auto-continue/pull/53) — fix(host): exclude child sessions from live recovery
<!-- OSS-CONTRIBUTIONS:END -->
