import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


class ModelConfigurationTests(unittest.TestCase):
    def test_skill_directory_uses_agy_name(self):
        skill_dir = PROJECT / ".agents" / "skills" / "agy-orchestrator"
        legacy_dir = skill_dir.parent / "codex-orchestrator"
        self.assertTrue(skill_dir.is_dir())
        self.assertFalse(legacy_dir.exists())
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^name: agy-orchestrator$")

    def test_skill_uses_invoke_subagent(self):
        skill_file = PROJECT / ".agents" / "skills" / "agy-orchestrator" / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("invoke_subagent", content)
        self.assertNotIn("spawn_agent", content)

    def test_template_directory_structure(self):
        templates_dir = PROJECT / "templates" / "agy"
        self.assertTrue((templates_dir / "config.toml").is_file())
        for role in ("explorer", "worker", "tester", "reviewer", "researcher"):
            self.assertTrue((templates_dir / "agents" / f"{role}.toml").is_file())


class ShellInstallerTests(unittest.TestCase):
    def run_installer(self, target, answers):
        result = subprocess.run(
            ["sh", str(PROJECT / "setup.sh")],
            input="\n".join((str(target), *answers, "")),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_default_installation(self):
        # Target path is first input, followed by Enters for all prompts
        # Prompts:
        # root model (default)
        # default subagent model (default)
        # explorer model (default)
        # worker model (default)
        # tester model (default)
        # reviewer model (default)
        # researcher model (default)
        # concurrency limit (default)
        # install .agy (y)
        # install skill (y)
        # install GEMINI.md (y)
        answers = [""] * 12
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.run_installer(target, answers)

            config_file = target / ".agy" / "config.toml"
            self.assertTrue(config_file.is_file())
            content = config_file.read_text(encoding="utf-8")
            self.assertIn('model = "gemini-3.1-pro-high"', content)
            self.assertIn('max_concurrent_threads_per_session = 4', content)

            for role in ("explorer", "worker", "tester", "reviewer", "researcher"):
                role_file = target / ".agy" / "agents" / f"{role}.toml"
                self.assertTrue(role_file.is_file())

            skill_file = (
                target / ".agents" / "skills" / "agy-orchestrator" / "SKILL.md"
            )
            self.assertTrue(skill_file.is_file())

            gemini_file = target / "GEMINI.md"
            self.assertTrue(gemini_file.is_file())
            self.assertIn("agy-orchestrator", gemini_file.read_text(encoding="utf-8"))

    def test_custom_numeric_models_and_concurrency(self):
        # 10: gemini-3.1-pro-high
        # 1: gemini-3.8-flash-high
        # 12: claude-sonnet-4-6
        # custom concurrency: 6
        answers = (
            "12",  # root: claude-sonnet-4-6
            "1",   # default subagent: gemini-3.8-flash-high
            "1",   # explorer: gemini-3.8-flash-high
            "10",  # worker: gemini-3.1-pro-high
            "1",   # tester: gemini-3.8-flash-high
            "12",  # reviewer: claude-sonnet-4-6
            "1",   # researcher: gemini-3.8-flash-high
            "6",   # concurrency: 6
            "y",   # install .agy
            "y",   # install skill
            "y",   # install GEMINI.md
        )
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.run_installer(target, answers)

            config = (target / ".agy" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "claude-sonnet-4-6"', config)
            self.assertIn('default_subagent_model = "gemini-3.8-flash-high"', config)
            self.assertIn("max_concurrent_threads_per_session = 6", config)

            reviewer = (target / ".agy" / "agents" / "reviewer.toml").read_text(
                encoding="utf-8"
            )
            self.assertIn('model = "claude-sonnet-4-6"', reviewer)

    def test_gemini_md_merging_preserves_content(self):
        existing_rule = "# Custom Project Guidelines\nAlways use tabs.\n"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "GEMINI.md").write_text(existing_rule, encoding="utf-8")

            answers = [""] * 12
            self.run_installer(target, answers)

            result = (target / "GEMINI.md").read_text(encoding="utf-8")
            self.assertIn("Always use tabs.", result)
            self.assertIn("agy-orchestrator", result)


class PowerShellInstallerTests(unittest.TestCase):
    executable = shutil.which("pwsh") or shutil.which("powershell")

    @unittest.skipUnless(executable, "PowerShell is not installed")
    def test_powershell_installer(self):
        answers = [""] * 12
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                [self.executable, "-NoProfile", "-File", str(PROJECT / "setup.ps1")],
                input="\n".join((str(target), *answers, "")),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            config = (target / ".agy" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "gemini-3.1-pro-high"', config)


if __name__ == "__main__":
    unittest.main()
