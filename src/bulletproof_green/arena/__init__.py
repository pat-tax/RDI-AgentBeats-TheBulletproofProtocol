"""Arena mode - Multi-turn adversarial narrative improvement.

This module orchestrates iterative refinement between Green (evaluator) and
Purple (generator) agents to improve narrative quality through critique-driven
iteration.

Uses messenger.py for Purple Agent communication (DRY principle).
"""

from bulletproof_green.arena.executor import (
    ArenaConfig,
    ArenaExecutor,
    ArenaResult,
    IterationRecord,
)

__all__ = [
    "ArenaConfig",
    "ArenaExecutor",
    "ArenaResult",
    "IterationRecord",
]
