"""Optional Gymnasium environment for verifier-in-the-loop discrete search."""

from __future__ import annotations

import random
from typing import Any

from .search import SearchEvaluator

try:
    import gymnasium as gym
    import numpy as np
    from gymnasium import spaces
except ImportError:  # Keep the core plugin usable without RL dependencies.
    gym = None
    np = None
    spaces = None


class QuantumDesignEnv(gym.Env if gym else object):
    """Set one design choice per action and reward deterministic verifier deltas."""

    metadata = {"render_modes": []}

    def __init__(self, search_space: dict[str, Any], seed: int = 0, max_steps: int | None = None):
        if gym is None or np is None or spaces is None:
            raise RuntimeError("Gymnasium is required; install scripts/requirements-search.txt")
        super().__init__()
        self.evaluator = SearchEvaluator(search_space, seed=seed)
        self.dimensions = self.evaluator.dimensions
        self.max_steps = max_steps or max(4, len(self.dimensions) * 3)
        self._rng = random.Random(seed)
        self._genome = [0 for _ in self.dimensions]
        self._steps = 0
        self._record: dict[str, Any] | None = None
        self.best_record: dict[str, Any] | None = None
        self._actions = [(dimension, value) for dimension, size in enumerate(self.dimensions) for value in range(size)]
        self.stop_action = len(self._actions)
        self.action_space = spaces.Discrete(self.stop_action + 1)
        self.observation_space = spaces.Box(0.0, 1.0, shape=(len(self.dimensions) + 4,), dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng.seed(seed)
        random_start = bool((options or {}).get("random_start", True))
        self._genome = [self._rng.randrange(size) if random_start else 0 for size in self.dimensions]
        self._steps = 0
        self._record = self.evaluator.evaluate(tuple(self._genome))
        self._update_best(self._record)
        return self._observation(), self._info()

    def step(self, action: int):
        if self._record is None:
            raise RuntimeError("reset() must be called before step()")
        previous_score = self.evaluator.scalar_score(self._record)
        terminated = int(action) == self.stop_action
        if not terminated:
            try:
                dimension, value = self._actions[int(action)]
            except (IndexError, ValueError) as exc:
                raise ValueError(f"invalid action: {action}") from exc
            self._genome[dimension] = value
            self._record = self.evaluator.evaluate(tuple(self._genome))
        self._steps += 1
        current_score = self.evaluator.scalar_score(self._record)
        reward = float(max(-100.0, min(100.0, current_score - previous_score)))
        truncated = self._steps >= self.max_steps
        self._update_best(self._record)
        return self._observation(), reward, terminated, truncated, self._info()

    def action_masks(self):
        """Mask no-op assignments while always allowing the explicit stop action."""
        mask = np.ones(self.stop_action + 1, dtype=bool)
        for action, (dimension, value) in enumerate(self._actions):
            if self._genome[dimension] == value:
                mask[action] = False
        mask[self.stop_action] = True
        return mask

    def _observation(self):
        genes = [gene / max(1, size - 1) for gene, size in zip(self._genome, self.dimensions)]
        metrics = self._record["metrics"]
        tail = [
            min(1.0, metrics.get("validation_errors", 0.0) / 10.0),
            min(1.0, metrics.get("claim_blockers", 0.0) / 10.0),
            min(1.0, metrics.get("validation_warnings", 0.0) / 10.0),
            metrics.get("proof_coverage", 0.0),
        ]
        return np.asarray(genes + tail, dtype=np.float32)

    def _info(self) -> dict[str, Any]:
        return {
            "candidate_id": self._record["candidate_id"],
            "genome": list(self._genome),
            "metrics": self._record["metrics"],
            "feasible": self._record["feasible"],
            "audit_verdict": self._record["audit_verdict"],
        }

    def _update_best(self, record: dict[str, Any]) -> None:
        if self.best_record is None or self.evaluator.scalar_score(record) > self.evaluator.scalar_score(self.best_record):
            self.best_record = record
