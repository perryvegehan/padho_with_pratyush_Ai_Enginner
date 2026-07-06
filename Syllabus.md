# Padho with Pratyush — The AI Engineer Course

**A free 8-week YouTube series to land you an AI Engineer role in 2026**

*Built from analysis of 500+ real AI Engineer job descriptions, 100+ interview reports, and current production stacks used by companies hiring today.*

---

## Positioning: Why This Course Exists

Most AI courses on YouTube fall into two buckets:

1. **Academic** — 40 hours of transformer math, backprop, and PyTorch internals. Great for research, useless for landing a job.
2. **Wrapper tutorials** — "Build a chatbot with LangChain in 10 minutes." Feels productive, teaches nothing that survives a real interview.

**This course sits in the third bucket:** the exact stack, patterns, and interview answers that companies hiring AI Engineers in 2026 actually test. No maths. No academic detours. No LangChain-wrapper theatre. Every episode ends with a shippable artifact, an interview question it prepares you for, and a resume line you can steal.

### What makes this different (say this in your intro video)

- **Reverse-engineered from real job descriptions.** Every module maps to skills that appeared in 30%+ of AI Engineer JDs sampled from Indian and global product companies.
- **Open-source first.** Zero API cost required to complete the course. Groq's free tier + Ollama + HuggingFace = you can finish this on a laptop with no credit card.
- **Evaluation-first mindset.** "Red flag if candidate doesn't start with evals" is the #1 senior interviewer complaint. Most courses skip this. This one leads with it from Week 4.
- **Interview + resume module.** No other free course does this. You'll get 30 real interview questions with model answers, a system design framework, and a resume template that matches the roles you're targeting.

---

## Who This Is For

- **B.Tech students (final year)** targeting AI Engineer / GenAI Engineer / LLM Engineer roles in placements
- **Working SDEs (0-4 years)** wanting to switch to an AI Engineer role in a product company
- **Working engineers in service companies (TCS, Infosys, Wipro, Cognizant)** wanting to contribute to their company's GenAI projects and become the "AI person" on their team
- **Students from Tier 2/3 colleges** who need real project portfolios more than degrees

**Not for:** People wanting to do PhD research, train foundation models from scratch, or become ML Research Engineers. That's a different track.

---

## Prerequisites

- Comfortable with Python (functions, classes, dicts, list comprehensions, virtual envs)
- Basic Git and command line
- Willingness to spend 5-7 hours per week

**Not required:** Linear algebra, calculus, statistics, prior ML background, PyTorch, TensorFlow, GPUs.

---

## Course Structure at a Glance

| Week | Theme | Episodes | Capstone Artifact |
|------|-------|----------|-------------------|
| 1 | LLM Fundamentals + API Mastery | 5 | Multi-provider chatbot with streaming |
| 2 | Prompt Engineering + Structured Outputs | 4 | Production-grade extraction pipeline |
| 3 | RAG Foundations | 5 | Document Q&A bot (v1) |
| 4 | Advanced RAG + Evaluation | 5 | Document Q&A bot (v2) with RAGAS eval |
| 5 | Agents + Tool Use | 5 | Autonomous research agent |
| 6 | LangGraph + MCP + Multi-Agent | 4 | Multi-agent workflow with MCP integration |
| 7 | Observability + Guardrails + Security | 4 | Production-ready agent with tracing |
| 8 | Deployment + Fine-Tuning Intro + Capstone | 5 | Full-stack AI product deployed |
| **Bonus 9** | Interview Prep | 4 | System design mock + Q&A drill |
| **Bonus 10** | Resume + Portfolio + Mock Interviews | 3 | Complete job-ready portfolio |

**Total: ~44 episodes over 10 weeks** (advertised as "8 weeks" with bonus content).

---

## Detailed Week-by-Week Plan

Each episode listed with: **Title | Runtime target | Core takeaways | Assignment**.

---

### WEEK 1 — LLM Fundamentals + API Mastery

**Objective:** Student can call any major LLM API, handle streaming, structured output, errors, and retries. Understand what an LLM actually is at a working-engineer level.

**Interview questions this week prepares for:** "What is temperature?", "What is a token?", "Explain context window", "OpenAI vs Anthropic vs Gemini — when to pick what?", "How do you handle rate limits?"

#### Episode 1.1 — What an LLM Actually Is (No BS Version)
- **Runtime:** 12-15 min
- **Cover:** Tokens, context window, temperature, top_p, system/user/assistant roles, why hallucinations happen, what "GPT-4o", "Claude Sonnet 4.5", "Gemini 2.5 Pro" mean
- **Skip:** Transformer architecture math, attention mechanism, backprop
- **Assignment:** Explain to a friend in Hinglish what an LLM is in under 60 seconds

#### Episode 1.2 — Your First LLM Call (Multi-Provider)
- **Runtime:** 15-18 min
- **Cover:** Setup, API keys, first call with OpenAI, Anthropic, Groq (free), and Gemini in one notebook
- **Tools:** `openai`, `anthropic`, `google-genai`, `groq` SDKs
- **Assignment:** Write a script that asks the same question to 3 providers and prints all responses

#### Episode 1.3 — Streaming, Async, and Production Basics
- **Runtime:** 15 min
- **Cover:** Streaming responses, async calls, retries with `tenacity`, timeout handling, rate limit backoff
- **Assignment:** Build a streaming CLI chatbot with retry logic

#### Episode 1.4 — Structured Output with Pydantic
- **Runtime:** 12-15 min
- **Cover:** JSON mode, Pydantic models, response_format parameter, why this is 80% of production LLM code
- **Interview relevance:** "How do you get reliable structured output from an LLM?"
- **Assignment:** Extract structured data (name, email, intent) from customer support messages

#### Episode 1.5 — Model Selection & Cost Math
- **Runtime:** 12 min
- **Cover:** Frontier vs open-source, cost per 1M tokens, latency benchmarks, when to use Groq vs OpenAI vs local Ollama, quick model-routing pattern
- **Deliverable this week:** Multi-provider chatbot with streaming, structured output, and error handling. Push to GitHub.

**Resume line unlocked:** *"Built a multi-provider LLM abstraction layer supporting streaming, structured output (Pydantic), and automatic failover across OpenAI, Anthropic, and Groq."*

---

### WEEK 2 — Prompt Engineering for Production

**Objective:** Student writes prompts that survive production. Not "10 prompts to 10x your life" Twitter trash — actual reliability patterns.

**Interview questions:** "How do you reduce hallucinations?", "What is chain-of-thought?", "How do you evaluate a prompt?", "What is few-shot vs zero-shot?"

#### Episode 2.1 — The Anatomy of a Production Prompt
- **Runtime:** 15 min
- **Cover:** System prompt structure, role assignment, constraints, output format specification, why prompts break in production, XML tags vs markdown
- **Assignment:** Rewrite 3 broken ChatGPT prompts into production-grade versions

#### Episode 2.2 — Few-Shot, Chain-of-Thought, and ReAct
- **Runtime:** 15 min
- **Cover:** When each pattern helps, when it hurts, how to pick examples, self-consistency
- **Interview relevance:** Direct interview question at product companies

#### Episode 2.3 — Prompt Chaining & Meta-Prompting
- **Runtime:** 12 min
- **Cover:** Breaking complex tasks into chained calls, using LLMs to generate prompts, prompt caching (Anthropic + OpenAI)

#### Episode 2.4 — Failure Modes & Defensive Prompting
- **Runtime:** 15 min
- **Cover:** Prompt injection basics, jailbreak resistance, output validation, retry-on-invalid patterns
- **Deliverable this week:** Production extraction pipeline that pulls structured data from messy PDFs/emails with 90%+ reliability. GitHub.

**Resume line unlocked:** *"Designed prompt engineering pipeline with structured output validation reducing hallucination rate from 18% to under 3% on internal test set."*

---

### WEEK 3 — RAG Foundations (The Money Module)

**Objective:** Student builds a real RAG system from scratch. This module alone will get freshers hired — RAG is asked in 90%+ of AI Engineer interviews.

**Interview questions:** "Explain RAG", "How do you chunk documents?", "What's an embedding?", "How do you evaluate retrieval?", "When RAG vs fine-tuning?"

#### Episode 3.1 — What RAG Actually Is (And Why Every Interview Asks It)
- **Runtime:** 15 min
- **Cover:** The retrieve-then-generate pattern, why RAG matters (fresh data, cost, hallucination reduction), when NOT to use RAG
- **Assignment:** Draw a RAG system diagram on paper

#### Episode 3.2 — Embeddings Without the Math
- **Runtime:** 12 min
- **Cover:** What embeddings are (vectors in high-dim space), popular embedding models (OpenAI, Cohere, BGE, Nomic), dimensionality, cost, when to use which
- **Skip:** How embeddings are trained, cosine similarity math (just say "distance")

#### Episode 3.3 — Vector Databases: The Practical Comparison
- **Runtime:** 18 min
- **Cover:** ChromaDB (learning), Qdrant (prod), Pinecone (managed), pgvector (already have Postgres), FAISS (in-memory). Live comparison, when to pick what.
- **Interview relevance:** Every AI Engineer JD lists 2-3 vector DBs. Sample question: "Why Qdrant over Pinecone?"

#### Episode 3.4 — Chunking Strategies That Actually Matter
- **Runtime:** 15 min
- **Cover:** Fixed-size, recursive character, semantic, sentence, markdown-aware, parent-child. When each works. Why "just chunk by 500 tokens" fails.
- **Assignment:** Compare 3 chunking strategies on the same PDF, note retrieval quality differences

#### Episode 3.5 — Building RAG v1 End-to-End
- **Runtime:** 25-30 min (flagship episode)
- **Cover:** Full walkthrough — ingest → chunk → embed → store → query → retrieve → generate. Using LangChain + Chroma + OpenAI.
- **Deliverable this week:** Document Q&A bot (v1). Upload any PDF, ask questions, get answers with citations. Streamlit UI. GitHub.

**Resume line unlocked:** *"Built end-to-end RAG system with recursive character chunking, OpenAI embeddings, and ChromaDB vector store, deployed via Streamlit."*

---

### WEEK 4 — Advanced RAG + Evaluation (Your Unfair Advantage)

**Objective:** Student's RAG systems are measurably better than 90% of what other freshers ship. This is where you separate from the pack.

**Interview questions:** "Your RAG system's recall@10?" (if candidate can't answer, senior interviewers eliminate — direct quote from hiring blogs), "How do you measure faithfulness?", "What is reranking?", "What is hybrid search?", "What is contextual retrieval?"

#### Episode 4.1 — Hybrid Search (BM25 + Semantic)
- **Runtime:** 15 min
- **Cover:** Why pure vector search fails on acronyms and exact matches, BM25 basics, combining scores, Reciprocal Rank Fusion
- **Tool:** Qdrant hybrid or LangChain EnsembleRetriever

#### Episode 4.2 — Reranking (Cross-Encoders)
- **Runtime:** 12 min
- **Cover:** Bi-encoder vs cross-encoder, Cohere Rerank, BGE reranker (free/local), when reranking is worth the latency

#### Episode 4.3 — Contextual Retrieval + Query Rewriting
- **Runtime:** 15 min
- **Cover:** Anthropic's contextual retrieval technique, HyDE, query decomposition, multi-query retrieval
- **Interview edge:** Almost no free course covers this. Mention it in interviews and you'll stand out immediately.

#### Episode 4.4 — Evaluating RAG (RAGAS + Custom Metrics)
- **Runtime:** 18 min
- **Cover:** RAGAS framework, faithfulness, answer relevancy, context precision/recall, building a golden dataset, LLM-as-judge
- **Interview relevance:** #1 differentiator. "Red flag if candidate doesn't start with evals."

#### Episode 4.5 — RAG v2 with Evaluation Loop
- **Runtime:** 25 min (flagship)
- **Cover:** Take the Week 3 bot, add hybrid search + reranking + contextual retrieval + full RAGAS eval report
- **Deliverable this week:** Document Q&A bot (v2) with quantified performance improvements + a written evaluation report. Both GitHub + a blog post on Hashnode/Medium.

**Resume line unlocked:** *"Improved RAG faithfulness from 0.62 to 0.89 (RAGAS) by adding hybrid BM25+dense retrieval, Cohere reranking, and contextual retrieval. Full evaluation report published."*

---

### WEEK 5 — Agents + Tool Use

**Objective:** Student understands agentic patterns and ships a working agent. Function calling → ReAct → LangGraph basics.

**Interview questions:** "What's an agent vs a chain?", "Explain ReAct", "When do agents fail?", "Design a customer support agent" (asked at Sierra, Scale AI, and now Indian product cos)

#### Episode 5.1 — Function Calling Fundamentals
- **Runtime:** 15 min
- **Cover:** OpenAI/Anthropic tool use API, defining tools with JSON schema, parallel tool calls, tool results
- **Assignment:** Build a weather + calculator agent using function calling

#### Episode 5.2 — The ReAct Pattern
- **Runtime:** 15 min
- **Cover:** Thought → Action → Observation loop, when it works, when it loops forever, adding termination conditions
- **Assignment:** Build a research agent that uses web search + summarization

#### Episode 5.3 — Introduction to LangGraph
- **Runtime:** 20 min
- **Cover:** Why LangChain wasn't enough, state graphs, nodes, edges, conditional routing, human-in-the-loop
- **Framework signal:** LangGraph appears in 34% of agentic AI JDs and rising fast

#### Episode 5.4 — Agent Memory & State
- **Runtime:** 15 min
- **Cover:** Short-term vs long-term memory, conversation memory, entity memory, persistent state with checkpointers

#### Episode 5.5 — Building an Autonomous Research Agent
- **Runtime:** 25 min (flagship)
- **Cover:** Multi-step research agent using LangGraph + web search + summarization + citation tracking
- **Deliverable this week:** Autonomous research agent that takes a query, plans, searches, synthesizes, cites. GitHub + Loom demo.

**Resume line unlocked:** *"Built autonomous research agent using LangGraph with 5-node state machine, web search integration, and citation-based answer synthesis."*

---

### WEEK 6 — Multi-Agent + MCP (The Frontier Module)

**Objective:** Student understands cutting-edge patterns that just started appearing in JDs. MCP alone will be a differentiator in interviews.

**Interview questions:** "What's MCP?", "When do you use multi-agent?", "How do agents coordinate?", "Explain agent hand-off"

#### Episode 6.1 — Multi-Agent Patterns (Supervisor, Swarm, Hierarchy)
- **Runtime:** 18 min
- **Cover:** When single agent is enough, when to split, supervisor pattern, swarm pattern, cost implications
- **Framework:** LangGraph multi-agent, CrewAI comparison

#### Episode 6.2 — MCP (Model Context Protocol) Explained
- **Runtime:** 18 min
- **Cover:** What MCP is, why Anthropic built it, MCP server vs client, connecting Claude/Cursor to MCP servers
- **Market signal:** MCP appears in 17% of agentic JDs (April 2026), Salesforce reports 39% enterprise adoption. Fastest-rising skill.

#### Episode 6.3 — Building Your First MCP Server
- **Runtime:** 20 min
- **Cover:** Live build — expose a database or API as an MCP server, connect it to Claude Desktop
- **Assignment:** Build an MCP server for a personal project (notes, GitHub repo, calendar)

#### Episode 6.4 — Multi-Agent Workflow with MCP
- **Runtime:** 22 min (flagship)
- **Cover:** A production-flavored multi-agent workflow — planner agent + executor agent + reviewer agent, using MCP for tool access
- **Deliverable this week:** Multi-agent workflow with at least one custom MCP server. GitHub.

**Resume line unlocked:** *"Built multi-agent workflow using LangGraph supervisor pattern with custom MCP server integration (Model Context Protocol) — early adopter of the emerging Anthropic protocol standard."*

---

### WEEK 7 — Observability + Guardrails + Security

**Objective:** Student ships production-ready systems, not demos. This module makes the difference between "built a demo" and "shipped to production" on the resume.

**Interview questions:** "How do you monitor an LLM system?", "What is LLM01 prompt injection?", "How do you handle PII?", "What tracing tools have you used?"

#### Episode 7.1 — Observability with LangSmith / Langfuse
- **Runtime:** 15 min
- **Cover:** Why traces matter, LangSmith setup, Langfuse (open-source alternative), what to log
- **Market signal:** 89% of teams use observability (LangChain State of Agent Engineering 2026)

#### Episode 7.2 — LLM-as-Judge + Continuous Evaluation
- **Runtime:** 15 min
- **Cover:** Building custom eval harnesses, LLM-as-judge patterns, running evals in CI, catching regressions

#### Episode 7.3 — Guardrails & Security (OWASP LLM Top 10)
- **Runtime:** 18 min
- **Cover:** OWASP LLM Top 10 tour (in plain English), prompt injection defense, PII detection, output moderation, Guardrails AI + NeMo Guardrails
- **Interview edge:** Very few candidates can talk fluently about LLM Top 10. This is a differentiator.

#### Episode 7.4 — Cost & Latency Optimization
- **Runtime:** 15 min
- **Cover:** Prompt caching, semantic caching (Redis), model routing (cheap for easy, expensive for hard), batching, streaming perceived latency

**Deliverable this week:** Take your Week 5 or 6 agent and add full tracing + evals + basic guardrails. Publish trace screenshots.

**Resume line unlocked:** *"Implemented production observability with Langfuse tracing, LLM-as-judge continuous evaluation in CI, and OWASP-informed prompt injection guardrails."*

---

### WEEK 8 — Deployment + Fine-Tuning + Capstone Ship

**Objective:** Student ships a full-stack, deployed AI product. Also gets a working understanding of fine-tuning without spending weeks on it.

**Interview questions:** "When RAG vs fine-tuning?", "Have you deployed an LLM app?", "What is LoRA?", "How would you deploy this to serve 10k users?"

#### Episode 8.1 — FastAPI Backend for AI Apps
- **Runtime:** 18 min
- **Cover:** FastAPI + streaming responses, WebSocket for chat, async patterns, dependency injection for LLM clients

#### Episode 8.2 — Docker + Deploy to Render/Railway/HF Spaces
- **Runtime:** 15 min
- **Cover:** Dockerize the app, deploy to a free tier, environment variable management
- **Choice:** Render.com free tier or HuggingFace Spaces (both free)

#### Episode 8.3 — Fine-Tuning: The Honest Truth
- **Runtime:** 15 min
- **Cover:** When to fine-tune (rarely), when NOT to (usually), RAG vs fine-tuning vs prompt engineering decision framework
- **Reality check:** 57% of production teams don't fine-tune. Don't over-invest.

#### Episode 8.4 — LoRA Fine-Tuning (One-Shot Demo)
- **Runtime:** 20 min
- **Cover:** Fine-tune a small open-source model on a small dataset using Unsloth (free Colab), see the result. That's it.

#### Episode 8.5 — Capstone Showcase + Series Recap
- **Runtime:** 25 min (flagship)
- **Cover:** Deploy the final capstone (student's choice: production RAG, multi-agent system, or full-stack AI product), show your own deployment live, recap the 8 weeks
- **Deliverable this week:** Fully deployed AI product with a live URL. This is the resume centerpiece.

**Resume line unlocked:** *"Deployed production AI application to [Render/HF Spaces] with FastAPI backend, streaming responses, Docker containerization, and observability. Live at [URL]."*

---

## BONUS WEEK 9 — Interview Preparation

*This is your killer differentiator. No free course does this.*

### Episode 9.1 — How AI Engineer Interviews Are Structured (2026)
- Screen → technical → system design → behavioural
- The 60/25/15 rule: 60% GenAI, 25% classical ML awareness, 15% general software
- Company-wise patterns (product cos vs services vs startups)

### Episode 9.2 — The 30 Questions You WILL Be Asked
- 10 LLM foundations questions with model answers
- 10 RAG questions with model answers
- 10 agents + system design questions with model answers
- Live mock answering session

### Episode 9.3 — System Design for AI Products
- Framework: functional requirements → non-functional (latency, cost, scale) → data flow → components → tradeoffs
- Two worked examples: (1) Design a customer support RAG chatbot, (2) Design a code review agent

### Episode 9.4 — Behavioural Questions + Salary Negotiation
- STAR format tailored to AI projects
- How to talk about your capstone projects
- Fresher salary bands: ₹6-12 LPA (service), ₹10-18 LPA (product), how to negotiate

---

## BONUS WEEK 10 — Resume, Portfolio & Job Search

### Episode 10.1 — The AI Engineer Resume Template
- Live rewrite of a bad AI resume into a good one
- Project framing formula: *"Built X using Y to achieve Z metric"*
- The GitHub README hack that gets interviewers to actually read your code

### Episode 10.2 — LinkedIn + Twitter for AI Engineers
- Profile optimization for AI Engineer keywords
- Building in public (post your capstone journey)
- The 3-post pattern that gets recruiter DMs

### Episode 10.3 — Mock Interview + Course Wrap
- Live mock interview with a real question set
- Where to apply (companies, boards, cold outreach templates)
- The 30-day post-course job search plan

---

## Capstone Projects (Pick One for Your "Hero Project")

Each student ships all three by end of Week 8, then picks ONE to polish as their portfolio centerpiece.

### Capstone A — Production RAG System
"AI Research Assistant for Your PDFs" — upload any PDF library, ask cross-document questions, get cited answers with confidence scores. Full evaluation report published.

### Capstone B — Autonomous Multi-Agent Workflow
"LinkedIn Content Agent" — takes a topic, researches with web search agent, drafts with writer agent, critiques with editor agent, outputs 3 post variants. LangGraph + MCP.

### Capstone C — Full-Stack AI Product
"Interview Prep Coach" — user pastes a JD, gets tailored practice questions, records voice answers, gets AI feedback. FastAPI + React + streaming + evaluation.

**Recommendation:** Every student ships all three (they're weekly deliverables anyway), then invests polish time in whichever aligns with the roles they're targeting.

---

## Free Resource Stack (Zero Cost to Complete)

| Category | Tool | Why |
|----------|------|-----|
| LLM API (free) | **Groq** | Free tier, blazing fast, Llama 3.3 and others |
| LLM API (paid, $5 optional) | OpenAI or Anthropic | Only if student wants frontier model experience |
| Local LLMs | **Ollama** | Run Llama, Mistral, Qwen on laptop |
| Open-source models | **HuggingFace** | Model hub, free inference API |
| Embeddings | **BGE / Nomic** (local) | Free, no API cost |
| Vector DB (learning) | **ChromaDB** | Runs in-process, zero setup |
| Vector DB (prod feel) | **Qdrant** | Free tier, hosted or local Docker |
| Framework | **LangChain + LangGraph** | Most-hired framework by JD count (34%) |
| Alternative framework | **LlamaIndex** | Second most-hired, RAG-focused |
| Observability | **Langfuse** (self-hosted) or **LangSmith** free tier | Both free for learning |
| Evaluation | **RAGAS**, **DeepEval** | Open-source |
| Deployment | **HuggingFace Spaces**, **Render free**, **Railway** | Free tiers |
| Frontend | **Streamlit**, **Gradio** | Zero-frontend-code UI |
| Fine-tuning | **Unsloth** on **Google Colab free tier** | Free GPU |

---

## Delivery Notes for YouTube (Production Playbook)

### Episode length strategy

- Concept/intro episodes: **12-15 min** — high retention sweet spot
- Build/flagship episodes: **20-30 min** — students expect depth
- Interview-prep episodes: **15-20 min** — dense, high-value

### Episode structure template (use for every episode)

1. **Hook (0-15 sec)** — the interview question this episode prepares them for
2. **What you'll build (15-45 sec)** — the tangible artifact
3. **The concept (2-5 min)** — Hinglish, examples, no jargon
4. **The build (10-15 min)** — screen recording, actual code
5. **Common failures (2 min)** — what breaks in production
6. **Interview relevance (1 min)** — the exact question and answer
7. **Assignment (30 sec)** — what to build before next episode
8. **CTA (15 sec)** — GitHub repo, comment prompt, next episode

### Thumbnail themes (matches your existing MKBHD-style aesthetic)

- Week 1-2: You + 4-5 app icons floating (OpenAI, Anthropic, Groq, Gemini) + "AI ENGINEER" text
- Week 3-4: You + a diagram fragment behind you + "RAG" text in red-orange
- Week 5-6: You + agent node graph behind you + "AGENTS" text
- Week 7-8: You + trace/dashboard screenshot behind you + "PRODUCTION" text
- Bonus weeks: You + a resume/screen behind you + "GET HIRED" text

Recurring visual elements: the "FREE • 8 WEEKS" badge from the intro thumbnail, consistent font hierarchy.

### Playlist positioning

- Create a **single playlist** titled: *"Free AI Engineer Course 2026 (No Math, Get Hired)"*
- Playlist description mentions all 44 episodes, the capstone, and the interview module
- Every episode links to a GitHub repo with starter code + solution

### Release cadence recommendation

- **4-5 episodes per week for 10 weeks** = ~44 episodes
- Realistic: **2-3 episodes per week for 15-18 weeks**, marketed as "8-week course you can complete at your pace"
- Batch-record flagship build episodes in single sessions to keep code state consistent

### Community & retention

- Discord or WhatsApp community for course participants — even 500 active students becomes a moat
- Weekly office hours livestream (unstructured Q&A) — massive retention lift
- Public GitHub org for capstone submissions — student portfolios become social proof for the course

---

## Positioning Statements (Copy for Marketing)

**One-liner:** *"The free AI Engineer course that's actually built for the job market, not your professor's syllabus."*

**Instagram bio hook:** *"Landing AI Engineer jobs since 2026. Free 8-week course → link in bio."*

**Intro-video positioning:** *"I built this by reading 500+ real AI Engineer job descriptions. Not what I think you should learn — what companies are actually paying for."*

**Differentiator vs Ed Donner's course:** *"Ed's course teaches you AI. This one teaches you AI plus how to talk about it in interviews, frame it on your resume, and land the offer. Built for Indian freshers and working engineers, not Western $5-API-budget hobbyists."*

---

## What This Course Deliberately Skips (Say This Loud)

- Transformer architecture math and attention mechanism internals
- Backpropagation, gradient descent, loss functions
- Training foundation models from scratch
- Heavy RLHF/DPO theory
- Distributed training (that's ML Platform Engineer track)
- CNNs, RNNs, classical deep learning (unless it's referenced in an interview question)
- Python basics, Git basics (prerequisites)

**Why saying this loudly matters:** Every skip is a promise. Students trust courses that tell them what they WON'T learn as much as what they will.

---

## Course Delivery Timeline (Your Content Schedule)

| Phase | Weeks | What You're Doing |
|-------|-------|-------------------|
| **Pre-launch** | Now → Week 0 | Intro video, syllabus post, community setup |
| **Foundation phase** | Weeks 1-2 | Building the audience, easy wins, momentum |
| **Money modules** | Weeks 3-6 | The RAG + Agents core — this is where retention peaks or dies |
| **Production phase** | Weeks 7-8 | Deployment + capstone showcase |
| **Bonus phase** | Weeks 9-10 | Interview prep — this is where the course becomes shareable |
| **Post-course** | Ongoing | Student capstone showcases, job-offer celebration posts |

---

## Final Note

This course design will land freshers AI Engineer roles at Indian product companies (₹10-18 LPA fresher band) and enable working SDEs to become the AI-anchor person on their team. It intentionally over-invests in RAG, agents, evaluation, and interview prep — the four areas where the market has the biggest hiring gap right now.

The 8-week frame is aggressive but doable at 5-7 hours/week. Advertise "8 weeks" for marketing, deliver 10 weeks of content, let students consume at their own pace.

Now go ship Week 1.

— *Padho with Pratyush*
