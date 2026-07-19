#!/usr/bin/env python3
"""Train an optional PPO policy over a finite QADL design space."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qadlib.environment import QuantumDesignEnv


def main() -> int:
    parser = argparse.ArgumentParser(description="Train Stable-Baselines3 PPO on a QADL search space")
    parser.add_argument("search_space")
    parser.add_argument("--steps", type=int, default=5_000)
    parser.add_argument("--algorithm", choices=("maskable-ppo", "ppo"), default="maskable-ppo")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model-out", default="qadl-ppo")
    parser.add_argument("--candidate-out", default="qadl-ppo-best.json")
    args = parser.parse_args()

    try:
        from stable_baselines3.common.env_checker import check_env
    except ImportError as exc:
        raise SystemExit("Install scripts/requirements-search.txt before running RL search") from exc

    search_space = json.loads(Path(args.search_space).read_text(encoding="utf-8"))
    env = QuantumDesignEnv(search_space, seed=args.seed)
    check_env(env, warn=True)
    if args.algorithm == "maskable-ppo":
        try:
            from sb3_contrib import MaskablePPO
        except ImportError as exc:
            raise SystemExit("Install sb3-contrib or select --algorithm ppo") from exc
        algorithm = MaskablePPO
    else:
        from stable_baselines3 import PPO

        algorithm = PPO
    model = algorithm("MlpPolicy", env, seed=args.seed, verbose=1)
    model.learn(total_timesteps=args.steps)
    model.save(args.model_out)
    if env.best_record is None:
        raise SystemExit("training completed without evaluating a candidate")
    Path(args.candidate_out).write_text(json.dumps(env.best_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"model: {args.model_out}.zip")
    print(f"best candidate: {args.candidate_out}")
    print("The policy score is search evidence, not a correctness proof or quantum-advantage certificate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
