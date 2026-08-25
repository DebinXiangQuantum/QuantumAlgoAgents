from __future__ import annotations

import builtins
import copy
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from qadlib import (  # noqa: E402
    analyze_resources,
    audit_advantage,
    render_formal_contract,
    render_qmd_handoff,
    search_candidates,
    validate_candidate,
    write_qmd_handoff,
)
from qadlib.expressions import ExpressionError, evaluate_expression  # noqa: E402


def load_example(name: str):
    return json.loads((PLUGIN_ROOT / "assets" / "examples" / name).read_text(encoding="utf-8"))


class QadlValidationTests(unittest.TestCase):
    def test_reference_candidate_is_valid_but_keeps_oracle_warning(self):
        report = validate_candidate(load_example("grover-oracle-search.qadl.json"))
        self.assertTrue(report["valid"])
        self.assertEqual(report["error_count"], 0)
        self.assertIn("expression.unknown", {item["code"] for item in report["issues"]})

    def test_expression_evaluator_rejects_code_execution(self):
        with self.assertRaises(ExpressionError):
            evaluate_expression("__import__('os').system('id')", {"N": 4})

    def test_resource_sampling_is_numeric_not_a_proof(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        report = analyze_resources(candidate, [{"N": 16}, {"N": 256}])
        self.assertEqual(report["points"][0]["resources"]["queries"], 3.0)
        self.assertIn("not an asymptotic proof", report["note"])

    def test_grover_example_schedule_meets_its_success_contract(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        expression = candidate["resources"]["expressions"]["queries"]
        for exponent in range(2, 14):
            size = 2**exponent
            rounds = int(evaluate_expression(expression, {"N": size}))
            theta = math.asin(1 / math.sqrt(size))
            success = math.sin((2 * rounds + 1) * theta) ** 2
            self.assertGreaterEqual(success, 2 / 3, f"N={size}, rounds={rounds}")

    def test_formal_renderer_preserves_latex_commands(self):
        rendered = render_formal_contract(load_example("grover-oracle-search.qadl.json"))
        self.assertIn(r"\text{Input access: }", rendered)
        self.assertIn(r"N: \nat_1", rendered)
        self.assertIn("input: INPUT", rendered)
        self.assertNotIn("\t", rendered)
        self.assertIn("do not constitute a machine-checked proof", rendered)

    def test_missing_jsonschema_fails_closed(self):
        real_import = builtins.__import__

        def import_without_jsonschema(name, *args, **kwargs):
            if name == "jsonschema" or name.startswith("jsonschema."):
                raise ImportError("blocked for fail-closed test")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_without_jsonschema):
            report = validate_candidate(load_example("grover-oracle-search.qadl.json"))
        self.assertFalse(report["valid"])
        self.assertIn("schema.unavailable", {item["code"] for item in report["issues"]})


class AdvantageAuditTests(unittest.TestCase):
    def test_query_claim_is_conditional_and_never_auto_certified(self):
        report = audit_advantage(load_example("grover-oracle-search.qadl.json"))
        self.assertEqual(report["blocker_count"], 0)
        self.assertIn("conditional-query", report["verdict"])
        self.assertFalse(report["automatic_certification"])

    def test_access_model_mismatch_blocks_claim(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        candidate["problem"]["classical_baselines"][0]["access_model"] = "explicit"
        report = audit_advantage(candidate)
        self.assertGreater(report["blocker_count"], 0)
        self.assertIn("audit.access-mismatch", {item["code"] for item in report["findings"]})

    def test_query_model_cannot_support_end_to_end_claim(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        candidate["claim"].update(
            {
                "type": "end-to-end-practical-advantage",
                "status": "empirically-observed",
                "scope": "end-to-end-wall-clock",
            }
        )
        report = audit_advantage(candidate)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("audit.resource-level", codes)
        self.assertIn("audit.full-cost", codes)

    def test_provable_query_claim_uses_query_resource_level(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        candidate["claim"].update({"type": "provable-speedup", "status": "formally-verified", "scope": "query"})
        for obligation in candidate["proof_obligations"]:
            if obligation["kind"] in {"correctness", "resource", "advantage"}:
                obligation["status"] = "formally-verified"
        report = audit_advantage(candidate)
        self.assertNotIn("audit.resource-level", {item["code"] for item in report["findings"]})


class SearchTests(unittest.TestCase):
    def test_evolutionary_search_is_seed_reproducible(self):
        search_space = load_example("grover-resource-tradeoff.search.json")
        first = search_candidates(search_space, method="evolutionary", budget=8, seed=11)
        second = search_candidates(search_space, method="evolutionary", budget=8, seed=11)
        first_ids = [item["candidate_id"] for item in first["archive"]]
        second_ids = [item["candidate_id"] for item in second["archive"]]
        self.assertEqual(first_ids, second_ids)
        self.assertEqual(first["search_space_size"], 2)
        self.assertEqual(first["archive_size"], 2)
        self.assertTrue(all(item["feasible"] for item in first["archive"]))

    def test_invalid_base_candidate_is_not_feasible(self):
        search_space = load_example("grover-resource-tradeoff.search.json")
        broken = copy.deepcopy(search_space)
        broken["base_candidate"]["problem"]["output"]["contract"] = "Different output"
        report = search_candidates(broken, method="random", budget=2, seed=0)
        self.assertTrue(all(not item["feasible"] for item in report["archive"]))


class QmdHandoffTests(unittest.TestCase):
    def test_qadl_status_does_not_create_a_qmd_proof(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        rendered = render_qmd_handoff(candidate)
        document = rendered["document"]
        self.assertFalse(rendered["machine_checked"])
        self.assertEqual(document.count(".theorem .goal"), len(candidate["proof_obligations"]))
        self.assertNotIn("{.proof", document)
        self.assertIn("Source QADL status: `proof-sketch`", document)
        self.assertIn("All black-box predicates with exactly one marked input", document)
        self.assertIn("success probability is `2 / 3`", document)
        self.assertIn("`randomized-black-box-scan` uses access `black-box-oracle`", document)
        self.assertIn("Its declared error budget is:", document)
        self.assertIn("Its resource-model assumptions are:", document)
        self.assertTrue(all(not item["proof_supplied"] for item in rendered["manifest"]["obligations"]))

    def test_explicit_proof_sidecar_maps_qadl_dependencies(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        rendered = render_qmd_handoff(
            candidate,
            {
                "po-resource": {
                    "text": "Under {{qadl-contract}}, counting the stated iterations gives the declared query expression.",
                    "draft": True,
                },
                "po-advantage": {
                    "text": "Under {{qadl-contract}} and by {{po-resource}}, the quantum upper bound has the claimed order.",
                },
            },
        )
        resource_id = next(
            item["qmd_id"] for item in rendered["manifest"]["obligations"] if item["qadl_id"] == "po-resource"
        )
        self.assertIn(f"@{resource_id}", rendered["document"])
        self.assertIn(f'@{rendered["manifest"]["qadl_contract_qmd_id"]}', rendered["document"])
        self.assertIn(".proof .draft", rendered["document"])
        self.assertNotIn("{{po-resource}}", rendered["document"])

    def test_handoff_refuses_to_replace_changed_protected_statements(self):
        candidate = load_example("grover-oracle-search.qadl.json")
        with TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".qmd-prover").mkdir()
            (project / "AGENTS.md").write_text(
                "<!-- qmd-prover-contract:start version=28 -->\n<!-- qmd-prover-contract:end -->\n",
                encoding="utf-8",
            )
            (project / ".qmd-prover" / "config.yml").write_text("verification:\n  backend: none\n", encoding="utf-8")
            (project / "_quarto.yml").write_text("book:\n  title: test\n  chapters: []\n", encoding="utf-8")
            first = write_qmd_handoff(candidate, project)
            self.assertTrue(first["exported"])
            self.assertEqual(first["quarto_chapter"], "added")
            self.assertTrue((project / "index.qmd").is_file())
            self.assertIn("index.qmd", (project / "_quarto.yml").read_text(encoding="utf-8"))

            changed = copy.deepcopy(candidate)
            changed["proof_obligations"][0]["statement"] += " Changed."
            with self.assertRaisesRegex(ValueError, "protected qmd statements"):
                write_qmd_handoff(changed, project)


class McpTests(unittest.TestCase):
    def test_stdio_server_lists_tools(self):
        messages = "\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
                "",
            ]
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "mcp_server.py")],
            input=messages,
            text=True,
            capture_output=True,
            check=True,
        )
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        names = {item["name"] for item in responses[1]["result"]["tools"]}
        self.assertIn("qadl_validate_candidate", names)
        self.assertIn("qadl_render_qmd_handoff", names)
        self.assertIn("qadl_search_candidates", names)

    def test_manifest_version_and_brand_assets_are_consistent(self):
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        server_source = (SCRIPTS / "mcp_server.py").read_text(encoding="utf-8")
        self.assertIn(f'"version": "{manifest["version"].split("+", 1)[0]}"', server_source)
        for field in ("composerIcon", "logo", "logoDark"):
            relative = manifest["interface"][field].removeprefix("./")
            self.assertTrue((PLUGIN_ROOT / relative).is_file(), field)


if __name__ == "__main__":
    unittest.main()
