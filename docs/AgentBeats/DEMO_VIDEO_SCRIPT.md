# The Bulletproof Protocol - Demo Video Script

**Duration**: 3 minutes
**Target**: AgentBeats Phase 1 Submission
**Recording Date**: January 31, 2026

---

## Setup & Prerequisites

**Before Recording:**
- Clear terminal history
- Set terminal font to 14pt+ for readability
- Record at 1080p minimum resolution
- Test microphone levels
- Have docker-compose running

**Tools:**
- Screen recording: OBS Studio / Loom / macOS built-in
- Terminal: iTerm2 or Terminal with high contrast theme
- Browser: For viewing JSON responses

---

## Script Timeline

### [0:00-0:30] Introduction & Setup (30 seconds)

**Visual**: Terminal with project root
**Audio**:

> "Welcome to The Bulletproof Protocol - the first agentified benchmark for IRS Section 41 R&D tax credit evaluation. This system addresses a critical gap: tax professionals spend over 4 hours manually reviewing each narrative, while current IRS AI achieves only 61% accuracy. Let's see how our agent-based benchmark automates this process."

**Commands**:
```bash
# Start the agent infrastructure
docker-compose up -d

# Verify green agent (Virtual Examiner)
curl http://localhost:8002/.well-known/agent-card.json | jq .

# Verify purple agent (R&D Substantiator)
curl http://localhost:8001/.well-known/agent-card.json | jq .
```

**Highlight**: Show AgentCard discovery - both agents are A2A-compatible

---

### [0:30-1:30] Narrative Generation (60 seconds)

**Visual**: Terminal showing purple agent narrative generation
**Audio**:

> "The purple agent generates R&D narratives using the Four-Part Test structure mandated by IRS Section 41. Each narrative documents: the technical hypothesis, experimental tests conducted, observed failures, and systematic iterations."

**Commands**:
```bash
# Generate a qualifying R&D narrative
curl -X POST http://localhost:8001/task \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "create_task",
    "params": {
      "task": {
        "project": "AI-Powered Fraud Detection System",
        "activity": "Novel neural architecture for real-time transaction analysis"
      }
    },
    "id": 1
  }' | jq .
```

**Highlight**:
- Show structured Four-Part Test format
- Point out technical uncertainty documentation
- Emphasize specificity and numeric evidence

**Audio Continuation**:
> "Notice the technical detail - specific hypothesis about neural architecture performance, quantified test results, documented failures, and systematic iteration. This is what distinguishes qualifying R&D from routine engineering."

---

### [1:30-2:30] Evaluation & Scoring (60 seconds)

**Visual**: Terminal showing green agent evaluation
**Audio**:

> "Now the green agent evaluates this narrative against IRS Section 41 statutory requirements using five weighted dimensions."

**Commands**:
```bash
# Submit narrative to green agent for evaluation
curl -X POST http://localhost:8002/task \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "create_task",
    "params": {
      "task": {
        "narrative": "[paste generated narrative]"
      }
    },
    "id": 1
  }' | jq .
```

**Highlight Components**:
1. **Routine Engineering Detection (30%)** - "No debugging or maintenance detected"
2. **Vagueness Detection (25%)** - "Strong numeric evidence present"
3. **Business Risk Detection (20%)** - "Clear technical vs commercial uncertainty"
4. **Experimentation Verification (15%)** - "Valid process of experimentation"
5. **Specificity Analysis (10%)** - "High technical detail"

**Audio**:
> "The system outputs a Risk Score of 8 out of 100 - well below the 20-point threshold for qualifying activities. The classification is QUALIFYING with 100% confidence. Each component provides transparency: where points were lost and why."

---

### [2:30-3:00] Agent Communication & Arena Mode (30 seconds)

**Visual**: Split screen showing both agents
**Audio**:

> "Both agents communicate via the A2A protocol using AgentCard discovery and JSON-RPC 2.0 tasks. This ensures reproducible, deterministic scoring. Phase 1 includes Arena Mode infrastructure for multi-turn refinement - the orchestration loop works, but narrative improvement logic is deferred to Phase 2 Purple Agent competition."

**Commands**:
```bash
# Show task status and final results
curl http://localhost:8002/task/[task_id] | jq .
```

**Highlight**:
- Task state: `pending → running → completed`
- Reproducible scoring (same input = same output)
- Component breakdown available for audit trail
- Arena Mode: Multi-turn loop functional, refinement deferred to Phase 2

**Audio Conclusion**:
> "Validation against 30 ground truth narratives shows 63% agreement with human labels - the 37% disagreements occur at borderline cases with risk scores near the 20-point threshold, exactly where benchmarks add value by exposing edge cases. This exceeds the IRS AI baseline of 61%, while providing deterministic, reproducible scoring. The architecture is Docker-packaged and publicly available on GitHub Container Registry."

**Visual**: Show final results summary with metrics

---

## Post-Production Checklist

- [ ] Add title slide: "The Bulletproof Protocol - AgentBeats Legal Track"
- [ ] Add captions for key metrics (63% accuracy on 30 narratives, 61% IRS baseline)
- [ ] Highlight edge cases as benchmark value (37% disagreements at borderline)
- [ ] Highlight important JSON fields (risk_score, classification)
- [ ] Add GitHub repo link overlay at end
- [ ] Total duration under 3 minutes
- [ ] Export at 1080p
- [ ] Upload to YouTube (unlisted/public)
- [ ] Add to submission form

---

## Key Talking Points

**Problem**:
- 4+ hours manual review per narrative
- IRS AI: 61.2% accuracy, 0.42 F1 score
- Inconsistent audit outcomes

**Solution**:
- Automated evaluation in 5 minutes
- 63% agreement with ground truth (disagreements expose valuable edge cases)
- Transparent rule-based scoring
- Adversarial agent competition

**Innovation**:
- First agentified tax compliance benchmark
- Reproducible legal evaluation
- A2A protocol integration
- Arena Mode framework ready (refinement in Phase 2)
- Generalizes to other compliance domains (SOC 2, HIPAA, GDPR)

---

## Technical Notes

**If demo fails:**
- Have backup recorded terminal session
- Keep pre-generated responses in snippets
- Practice dry run 3x before recording

**Response times:**
- Narrative generation: ~30 seconds
- Evaluation: ~5 seconds
- Allow buffer time for API calls

**Error handling:**
- If agents aren't responding, show `docker-compose logs`
- If API error, explain and retry with backup command
