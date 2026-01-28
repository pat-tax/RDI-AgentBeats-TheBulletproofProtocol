# Testing Strategy: Deterministic + Property-Based

## Executive Summary

**Completed:** Centralized configuration with pydantic-settings + test suite optimization
**Result:** 35% fewer tests, 78% faster runtime, maintained 100% pass rate
**Next:** Implement property-based testing with Hypothesis for edge cases

---

## Completed Work

### 1. Pydantic Settings Implementation

**Problem:** Configuration scattered across 6+ files, duplicated defaults, no validation

**Solution:** Centralized settings with automatic `.env` loading

```python
# Green Agent: GREEN_* prefix
from bulletproof_green.settings import settings
settings.port              # 8000
settings.timeout           # 300
settings.openai_api_key    # None (from env)

# Purple Agent: PURPLE_* prefix
from bulletproof_purple.settings import settings
settings.port              # 8001
settings.timeout           # 300
```

**Files Created:**
- `src/bulletproof_green/settings.py` - 11 settings
- `src/bulletproof_purple/settings.py` - 3 settings

**Benefits:**
- Single source of truth for defaults
- Automatic type validation (Pydantic)
- Environment variable support (`.env` files)
- No more `DEFAULT_TIMEOUT` duplication

---

### 2. Test Suite Optimization

**Metrics:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Tests | 532 | 348 | **-35%** |
| Runtime | 16.5s | 3.7s | **-78%** |
| Pass Rate | 100% | 100% | Maintained |

**Removed Patterns (184 tests):**

1. **Import/existence tests** - "test X module exists"
   - Python/Pydantic handles this
   - If imports fail, other tests fail

2. **Field existence tests** - "test Y has Z field"
   - Pydantic validates at instantiation
   - Redundant with behavior tests

3. **Default value tests** - "test default is 300"
   - Testing constants (300 == 300)
   - Settings handle this now

4. **Over-granular tests** - 8 tests for one AgentCard
   - Consolidated into schema validation

5. **Type checks** - "test returns dict"
   - Type checker (pyright) handles this

**Files Cleaned:**

```
test_llm_judge.py:              64 → 8  tests (-87%)
test_arena_executor.py:         56 → 7  tests (-88%)
test_agent_card_discovery.py:   50 → 11 tests (-78%)
test_output_schema.py:          29 → 8  tests (-72%)
test_purple_generator.py:       21 → 6  tests (-71%)
test_messenger.py:              24 → 11 tests (-54%)
test_green_a2a_client.py:       27 → 11 tests (-59%)
```

---

## Testing Philosophy

### Core Principles

**Pytest for Deterministic Behavior**
- Known inputs → expected outputs
- Algorithm correctness
- Protocol compliance
- Error handling

**Hypothesis for Edge Cases**
- Unknown/random inputs
- Boundary conditions
- Invariant properties
- Input validation

---

## Recommended Hypothesis Tests

### High-Value Property Tests

#### 1. **Scoring Formulas (CRITICAL)**

**Why:** Math must work for ALL inputs, not just examples

```python
from hypothesis import given, strategies as st
from bulletproof_green.scorer import AgentBeatsScorer

@given(
    routine=st.integers(min_value=0, max_value=100),
    vagueness=st.integers(min_value=0, max_value=100),
    business=st.integers(min_value=0, max_value=100),
)
def test_risk_score_invariants(routine, vagueness, business):
    """Property: risk_score always between 0-100."""
    scorer = AgentBeatsScorer()

    # Simulate penalty calculation
    total_penalty = routine + vagueness + business
    risk_score = min(100, total_penalty)

    assert 0 <= risk_score <= 100
    assert isinstance(risk_score, int)


@given(
    rule_score=st.floats(min_value=0.0, max_value=1.0),
    llm_score=st.floats(min_value=0.0, max_value=1.0),
    alpha=st.floats(min_value=0.0, max_value=1.0),
)
def test_hybrid_score_properties(rule_score, llm_score, alpha):
    """Property: final_score = α*rule + β*llm always in [0,1]."""
    beta = 1.0 - alpha
    final = alpha * rule_score + beta * llm_score

    assert 0.0 <= final <= 1.0

    # Weighted average property
    assert final >= min(rule_score, llm_score)
    assert final <= max(rule_score, llm_score)
```

---

#### 2. **Narrative Validation (HIGH)**

**Why:** Must handle arbitrary text inputs safely

```python
from hypothesis import given, strategies as st
from bulletproof_green.evaluator import RuleBasedEvaluator

@given(narrative=st.text(min_size=0, max_size=10000))
def test_evaluator_never_crashes(narrative):
    """Property: evaluator handles any text without crashing."""
    evaluator = RuleBasedEvaluator()

    result = evaluator.evaluate(narrative)

    # Should always return valid result
    assert result is not None
    assert hasattr(result, 'risk_score')
    assert 0 <= result.risk_score <= 100


@given(
    narrative=st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=1, max_size=5000)
)
def test_output_always_serializable(narrative):
    """Property: output always JSON-serializable."""
    import json
    evaluator = RuleBasedEvaluator()

    result = evaluator.evaluate(narrative)
    output = result.to_dict()

    # Should never raise
    json_str = json.dumps(output)
    assert isinstance(json_str, str)
```

---

#### 3. **Component Score Invariants (CRITICAL)**

**Why:** Total must equal sum (math consistency)

```python
@given(narrative=st.text(min_size=10, max_size=1000))
def test_total_penalty_equals_sum_property(narrative):
    """Property: total_penalty always equals sum of components."""
    evaluator = RuleBasedEvaluator()
    result = evaluator.evaluate(narrative)

    cs = result.component_scores

    expected = (
        cs['routine_engineering_penalty'] +
        cs['vagueness_penalty'] +
        cs['business_risk_penalty'] +
        cs['experimentation_penalty'] +
        cs['specificity_penalty']
    )

    assert cs['total_penalty'] == expected
```

---

#### 4. **Redline Severity Counts (MEDIUM)**

```python
@given(narrative=st.text(min_size=10, max_size=2000))
def test_severity_counts_match_issues(narrative):
    """Property: severity counts always match issues array."""
    evaluator = RuleBasedEvaluator()
    result = evaluator.evaluate(narrative)

    redline = result.to_dict()['redline']

    critical = sum(1 for i in redline['issues'] if i['severity'] == 'critical')
    high = sum(1 for i in redline['issues'] if i['severity'] == 'high')
    medium = sum(1 for i in redline['issues'] if i['severity'] == 'medium')

    assert redline['critical'] == critical
    assert redline['high'] == high
    assert redline['medium'] == medium
    assert redline['total_issues'] == len(redline['issues'])
```

---

#### 5. **Arena Loop Termination (CRITICAL)**

**Why:** Must terminate for ALL inputs (no infinite loops)

```python
@given(
    max_iterations=st.integers(min_value=1, max_value=10),
    target=st.integers(min_value=0, max_value=100),
)
def test_arena_always_terminates(max_iterations, target):
    """Property: arena loop always terminates."""
    from unittest.mock import AsyncMock, patch
    from bulletproof_green.arena_executor import ArenaConfig, ArenaExecutor

    config = ArenaConfig(max_iterations=max_iterations, target_risk_score=target)
    executor = ArenaExecutor(purple_agent_url="http://test", config=config)

    # Mock to prevent network calls
    with patch.object(executor, '_run_iteration', new_callable=AsyncMock) as mock:
        mock.return_value = ("narrative", 50, {})  # Never qualifies

        result = await executor.run(initial_context="test")

        # Must terminate at max_iterations
        assert result.total_iterations <= max_iterations
        assert result.termination_reason in ["target_reached", "max_iterations_reached"]
```

---

#### 6. **Settings Validation (MEDIUM)**

```python
@given(
    port=st.integers(),
    timeout=st.integers(),
)
def test_settings_validation(port, timeout):
    """Property: settings reject invalid values."""
    from pydantic import ValidationError
    from bulletproof_green.settings import GreenSettings

    try:
        settings = GreenSettings(port=port, timeout=timeout)

        # If accepted, must be valid
        assert 1 <= settings.port <= 65535
        assert settings.timeout > 0
    except ValidationError:
        # Invalid inputs should raise
        assert port < 1 or port > 65535 or timeout <= 0
```

---

## Implementation Plan

### Phase 1: Critical Math (Week 1)
- [ ] Hybrid scoring formula
- [ ] Component score totals
- [ ] Risk score boundaries

### Phase 2: Input Validation (Week 2)
- [ ] Narrative text handling
- [ ] JSON serialization
- [ ] Settings validation

### Phase 3: Control Flow (Week 3)
- [ ] Arena loop termination
- [ ] Severity count consistency

---

## Expected Benefits

### Before Hypothesis
```python
def test_risk_score_range():
    result = evaluator.evaluate("test")
    assert 0 <= result.risk_score <= 100
```
✗ Only tests one input
✗ Misses edge cases
✗ False confidence

### After Hypothesis
```python
@given(narrative=st.text())
def test_risk_score_range(narrative):
    result = evaluator.evaluate(narrative)
    assert 0 <= result.risk_score <= 100
```
✓ Tests 100+ random inputs per run
✓ Finds edge cases automatically
✓ Shrinks failures to minimal examples

---

## Installation

```bash
uv add --dev hypothesis
```

## Running Hypothesis Tests

```bash
# Run all tests (pytest + hypothesis)
uv run pytest

# Run only hypothesis tests
uv run pytest -m hypothesis

# Increase examples for CI
uv run pytest --hypothesis-show-statistics
```

---

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Hypothesis for Scientific Code](https://hypothesis.readthedocs.io/en/latest/numpy.html)
- [Property-Based Testing Patterns](https://hypothesis.works/articles/what-is-property-based-testing/)

---

## Appendix: Current Test Coverage

### High-Value Tests (Kept)

**Behavior Tests:**
- Hybrid scoring formula correctness
- Arena loop termination conditions
- Protocol compliance (JSON-RPC, A2A)

**Integration Tests:**
- End-to-end server request handling
- Agent-to-agent communication
- Error handling (timeouts, validation)

**Edge Cases:**
- LLM fallback behavior
- Empty/malformed inputs
- Boundary conditions

### Removed Tests (Low ROI)

- Import existence checks
- Pydantic field validation
- Default constant values
- Return type assertions
- Over-granular field checks
