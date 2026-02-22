# AgentBeats Competition Alignment

> **Purpose:** Documents how this project addresses AgentBeats competition vision and premises
>
> **See also:**
> - [ABSTRACT.md](ABSTRACT.md) - Benchmark methodology and validation results
> - [SUBMISSION-GUIDE.md](SUBMISSION-GUIDE.md) - Requirements and judging criteria
> - [TODO.md](../TODO.md) - Phase 1 vs Phase 2 scope boundaries

---

## Competition Vision: The 4 Problems

AgentBeats addresses critical gaps in agentic AI evaluation:

### 1. Interoperability
**Problem:** Production agents require substantial modifications to run on existing benchmarks

**Our Solution:** A2A protocol for universal agent-to-agent communication
- ✅ AgentCard discovery at `/.well-known/agent-card.json`
- ✅ JSON-RPC 2.0 task lifecycle
- ✅ Any A2A-compatible agent can be evaluated without modification

### 2. Reproducibility
**Problem:** Stateful tools and dynamic configurations cause result variance across runs

**Our Solution:** Deterministic evaluation with statistical validation
- ✅ Rule-based detection (no LLM non-determinism in Phase 1)
- ✅ Fresh state per task (stateless agents)
- ✅ Cohen's κ and 95% confidence intervals for benchmark credibility

**See:** [LIMITATIONS.md](LIMITATIONS.md#reproducibility-constraints) for detailed analysis

### 3. Fragmentation
**Problem:** Leaderboards and results scattered across platforms

**Our Solution:** AgentBeats platform integration
- ✅ AgentBeats-compatible output schema
- ✅ `scenario.toml` configuration for platform orchestration
- ✅ Public GHCR images for centralized access

### 4. Discovery
**Problem:** Finding relevant benchmarks is time-consuming

**Our Solution:** Standardized discovery mechanisms
- ✅ AgentCard self-description (capabilities, endpoints)
- ✅ Public Docker images on GitHub Container Registry
- ✅ Open-source repository for transparency

---

## Track Selection: Legal Domain

**Chosen Track:** Create New Benchmark - Legal Domain Agent

**Rationale:** IRS Section 41 R&D tax credit evaluation addresses a critical automation gap in legal compliance. Current IRS AI achieves only 61.2% accuracy, creating significant compliance risk.

**See:** [ABSTRACT.md](ABSTRACT.md) for complete problem statement and validation results

---

## Phase 1 Focus: Green Agent

**In Scope (Phase 1 - Green Agent Benchmark):**
- ✅ Rule-based evaluation engine (5 weighted dimensions)
- ✅ Automated scoring (Risk Score 0-100, binary classification)
- ✅ Ground truth dataset (30 narratives, difficulty tiers)
- ✅ Statistical validation (Cohen's κ, confidence intervals)
- ✅ Baseline purple agent demonstrating benchmark usage
- ✅ Docker deployment (linux/amd64, GHCR)

**Deferred (Phase 2 - Purple Agent Competition):**
- ⏸️ Arena Mode (multi-turn adversarial refinement)
- ⏸️ Hybrid LLM evaluation (semantic analysis)
- ⏸️ SSE task streaming (real-time updates)
- ⏸️ ART fine-tuning pipeline (purple agent training)

**See:** [TODO.md](../TODO.md#-deferred---phase-2-feb-march-2026) for complete deferral list with rationale

---

## Alignment with Judging Criteria

All 5 judging criteria addressed in implementation:

1. **Technical Correctness** ✅ - Clean code, Docker builds, error handling
2. **Reproducibility** ✅ - Deterministic scoring, consistent results
3. **Benchmark Design Quality** ✅ - Realistic tasks, difficulty tiers, agentic capabilities
4. **Evaluation Methodology** ✅ - Clear scoring, 5 dimensions, nuanced evaluation
5. **Innovation & Impact** ✅ - First agentified tax compliance benchmark, addresses IRS AI gap

**See:** [SUBMISSION-GUIDE.md](SUBMISSION-GUIDE.md#judging-criteria) for detailed criteria breakdown

---

## Key Differentiators

1. **Legal Domain First:** First agentified benchmark for tax compliance evaluation
2. **Practical Impact:** Reduces 4-hour manual reviews to 5-minute automated evaluations
3. **Statistical Rigor:** Goes beyond Phase 1 requirements with Cohen's κ and held-out test sets
4. **Domain Transfer:** Architecture generalizes to other legal compliance domains (SOC 2, HIPAA, GDPR)

**See:** [ABSTRACT.md](ABSTRACT.md#key-innovations) for validation results and comparative analysis

---

**Last Updated:** 2026-01-31
**Competition Deadline:** Phase 1 - January 31, 2026
