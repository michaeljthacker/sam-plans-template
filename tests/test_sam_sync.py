"""End-to-end tests for plans/sam-install.py, plans/sam-update.py, and plans/sam_sync.py.

Template-repo only: this folder is not in the sync manifest and is never
installed into projects. Run from the repo root:

    python -m unittest discover -s tests -v

Each test builds a throwaway Git project in a temp directory and drives the
real entry points as subprocesses, exactly as a user would.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "plans" / "sam-install.py"
SEVEN = [
    "plans/BACKLOG.md",
    "plans/BUILD.md",
    "plans/CHANGELOG.md",
    "plans/DECISIONS.md",
    "plans/MILESTONE.md",
    "plans/STANDARDS.md",
    "plans/VISION.md",
]
LEGACY_REF = "v1.8.0-legacy"  # resolved in setUpModule

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}


def sh(args: list[str], cwd: Path, stdin: str = "", check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=GIT_ENV)
    if check and r.returncode not in (0, 2):
        raise AssertionError(f"{args} failed ({r.returncode}):\n{r.stdout}\n{r.stderr}")
    return r


def git(cwd: Path, *args: str) -> str:
    return sh(["git", "-c", "core.autocrlf=false", *args], cwd).stdout


def install(cwd: Path, *flags: str) -> subprocess.CompletedProcess:
    return sh([sys.executable, str(INSTALL), *flags], cwd)


def update(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return sh([sys.executable, str(cwd / "plans" / "sam-update.py"), *args], cwd, check=check)


def tracked(cwd: Path) -> set[str]:
    return set(filter(None, git(cwd, "ls-files").splitlines()))


class ProjectCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="sam-test-"))
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        git(self.proj, "init", "-q")
        (self.proj / "app.py").write_text("print('hi')\n")
        (self.proj / ".gitignore").write_text("node_modules/\n")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "init")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit_all(self, msg: str = "c") -> None:
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", msg)


class FreshInstall(ProjectCase):
    def test_installs_full_environment(self):
        r = install(self.proj)
        self.assertEqual(r.returncode, 0, r.stdout)
        for rel in ["plans/README.md", "plans/templates/registry.json", "plans/sam-update.py",
                    "plans/sam_sync.py", "plans/config.json", "plans/state.json", "plans/thread.md",
                    "plans/STATUS.md", "plans/.sam-version", "CLAUDE.md",
                    ".github/copilot-instructions.md", *SEVEN]:
            self.assertTrue((self.proj / rel).is_file(), rel)
        state = json.loads((self.proj / "plans/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["next_action_id"], "Product.ProductVision")
        self.assertIn("ignore rules verified", r.stdout)

    def test_only_seven_plans_files_are_trackable(self):
        install(self.proj)
        self.commit_all()
        self.assertEqual(tracked(self.proj), {".gitignore", "app.py", *SEVEN})

    def test_gitignore_block_preserves_project_rules(self):
        install(self.proj)
        text = (self.proj / ".gitignore").read_text()
        self.assertTrue(text.startswith("node_modules/\n"))
        self.assertIn("# BEGIN SAM MANAGED\n/plans/*\n!/plans/BACKLOG.md\n", text)
        self.assertIn("/CLAUDE.md\n/.github/copilot-instructions.md\n# END SAM MANAGED\n", text)

    def test_crlf_gitignore_keeps_line_endings(self):
        (self.proj / ".gitignore").write_bytes(b"node_modules/\r\ndist/\r\n")
        install(self.proj)
        data = (self.proj / ".gitignore").read_bytes()
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertTrue(data.startswith(b"node_modules/\r\ndist/\r\n"))

    def test_idempotent(self):
        install(self.proj)
        self.commit_all()
        before = (self.proj / ".gitignore").read_bytes()
        r = install(self.proj)
        self.assertEqual((self.proj / ".gitignore").read_bytes(), before)
        self.assertIn("SAM block is current", r.stdout)
        self.assertIn("created:             0", r.stdout)
        self.assertEqual(git(self.proj, "status", "--porcelain"), "")
        r = update(self.proj, "--apply")
        self.assertEqual(git(self.proj, "status", "--porcelain"), "")

    def test_block_replaced_in_place_not_moved(self):
        install(self.proj)
        gi = self.proj / ".gitignore"
        gi.write_text(gi.read_text() + "*.log\n")
        install(self.proj)
        self.assertTrue(gi.read_text().endswith("# END SAM MANAGED\n*.log\n"))

    def test_rule_after_block_that_defeats_policy_is_reported(self):
        install(self.proj)
        gi = self.proj / ".gitignore"
        gi.write_text(gi.read_text() + "*.md\n")
        r = install(self.proj)
        self.assertEqual(r.returncode, 2)
        self.assertIn("plans/BUILD.md should be trackable", r.stdout)

    def test_malformed_markers_fail_safely(self):
        (self.proj / ".gitignore").write_text("# BEGIN SAM MANAGED\n/plans/*\n")
        r = sh([sys.executable, str(INSTALL)], self.proj, check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("malformed SAM markers", r.stderr)

    def test_dry_run_writes_nothing(self):
        r = install(self.proj, "--dry-run")
        self.assertIn("DRY-RUN", r.stdout)
        self.assertFalse((self.proj / "plans").exists())
        self.assertEqual((self.proj / ".gitignore").read_text(), "node_modules/\n")


class Preservation(ProjectCase):
    def test_instance_files_never_overwritten(self):
        install(self.proj)
        custom = {
            "plans/BUILD.md": "# my build\n",
            "plans/VISION.md": "my vision\n",
            "plans/STATUS.md": "my status\n",
            "plans/thread.md": "my thread\n",
            "plans/config.json": json.dumps({"code_review": "every_phase"}) + "\n",
            "plans/state.json": json.dumps({"next_action_id": "Staff.DraftQuestions"}) + "\n",
        }
        for rel, text in custom.items():
            (self.proj / rel).write_text(text)
        install(self.proj)
        update(self.proj, "--apply")
        for rel, text in custom.items():
            self.assertEqual((self.proj / rel).read_text(), text, rel)

    def test_system_file_edits_are_refreshed_with_visible_diff(self):
        install(self.proj)
        (self.proj / "plans/FORMATS.md").write_text("local edit\n")
        r = update(self.proj)
        self.assertIn("[will update] plans/FORMATS.md", r.stdout)
        self.assertIn("-local edit", r.stdout)
        self.assertEqual((self.proj / "plans/FORMATS.md").read_text(), "local edit\n")


class Migration(ProjectCase):
    def legacy_layout(self):
        """A pre-2.0 project: all of plans/ copied in and committed."""
        shutil.copytree(REPO / "plans", self.proj / "plans",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(REPO / "plans/CLAUDE.md", self.proj / "CLAUDE.md")
        (self.proj / ".github").mkdir()
        shutil.copy(REPO / "plans/copilot-instructions.md", self.proj / ".github/copilot-instructions.md")
        (self.proj / ".github/workflows.yml").write_text("ci\n")
        self.commit_all("legacy")

    def test_update_untracks_sam_files_and_keeps_local_copies(self):
        self.legacy_layout()
        r = update(self.proj, str(REPO), "--apply", "--untrack")
        self.assertIn("untracked", r.stdout)
        self.assertEqual(
            tracked(self.proj),
            {".gitignore", "app.py", ".github/workflows.yml", *SEVEN},
        )
        for rel in ["plans/state.json", "plans/README.md", "CLAUDE.md", ".github/copilot-instructions.md"]:
            self.assertTrue((self.proj / rel).is_file(), rel)
        self.commit_all("migrate")
        self.assertEqual(git(self.proj, "status", "--porcelain"), "")
        self.assertEqual(len(git(self.proj, "log", "--oneline").splitlines()), 3)  # no rewrite

    def test_noninteractive_without_flag_leaves_index_alone(self):
        self.legacy_layout()
        before = tracked(self.proj)
        r = update(self.proj, str(REPO), "--apply")
        self.assertIn("Rerun with --untrack", r.stdout)
        self.assertEqual(tracked(self.proj), before)

    def test_dry_run_reports_candidates_without_touching_index(self):
        self.legacy_layout()
        before = tracked(self.proj)
        r = update(self.proj, str(REPO))
        self.assertIn("plans/state.json", r.stdout)
        self.assertIn("on apply you will be offered", r.stdout)
        self.assertEqual(tracked(self.proj), before)

    def test_install_on_legacy_project_also_migrates(self):
        self.legacy_layout()
        install(self.proj, "--untrack")
        self.assertEqual(tracked(self.proj), {".gitignore", "app.py", ".github/workflows.yml", *SEVEN})

    def test_v180_updater_bootstraps_new_engine(self):
        """A project's own pre-2.0 sam-update.py pulls in the 2.0 engine; a rerun finishes."""
        try:
            legacy = git(REPO, "show", f"{LEGACY_REF}:plans/sam-update.py")
        except AssertionError:
            self.skipTest("v1.8.0 sam-update.py not available in git history")
        self.legacy_layout()
        (self.proj / "plans/sam_sync.py").unlink()
        (self.proj / "plans/sam-install.py").unlink()
        (self.proj / "plans/sam-update.py").write_text(legacy, encoding="utf-8")
        update(self.proj, str(REPO), "--apply")
        self.assertTrue((self.proj / "plans/sam_sync.py").is_file())
        stamp = json.loads((self.proj / "plans/.sam-version").read_text(encoding="utf-8"))
        self.assertIn("legacy-bootstrap", stamp["manifest_version"])
        r = update(self.proj, "--apply", "--untrack")  # source now read from .sam-version
        self.assertIn("SAM update", r.stdout)
        stamp = json.loads((self.proj / "plans/.sam-version").read_text(encoding="utf-8"))
        self.assertEqual(stamp["manifest_version"], "2.0.0")
        self.assertEqual(tracked(self.proj), {".gitignore", "app.py", ".github/workflows.yml", *SEVEN})


class RootBootstrapFiles(ProjectCase):
    def test_custom_claude_md_is_kept_tracked_and_not_ignored(self):
        (self.proj / "CLAUDE.md").write_text("Project-specific guidance.\n")
        self.commit_all()
        r = install(self.proj, "--untrack")
        self.assertIn("[custom]    CLAUDE.md", r.stdout)
        self.assertEqual((self.proj / "CLAUDE.md").read_text(), "Project-specific guidance.\n")
        self.assertNotIn("/CLAUDE.md\n", (self.proj / ".gitignore").read_text())
        self.assertIn("CLAUDE.md", tracked(self.proj))
        update(self.proj, "--apply")  # later updates keep honoring it
        self.assertEqual((self.proj / "CLAUDE.md").read_text(), "Project-specific guidance.\n")

    def test_force_replaces_custom_file(self):
        (self.proj / "CLAUDE.md").write_text("Project-specific guidance.\n")
        install(self.proj, "--force")
        self.assertEqual((self.proj / "CLAUDE.md").read_bytes(), (REPO / "plans/CLAUDE.md").read_bytes())
        self.assertIn("/CLAUDE.md\n", (self.proj / ".gitignore").read_text())


class Guards(ProjectCase):
    def test_refuses_template_source_repo(self):
        (self.proj / ".sam-template-source").write_text("x\n")
        r = sh([sys.executable, str(INSTALL)], self.proj, check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("template source repo", r.stderr)

    def test_installed_copy_of_installer_refuses_to_target_itself(self):
        install(self.proj)
        r = sh([sys.executable, str(self.proj / "plans/sam-install.py")], self.proj, check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("same directory", r.stderr)

    def test_non_git_target(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        r = install(plain)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("index migration skipped", r.stdout)
        self.assertIn("# BEGIN SAM MANAGED", (plain / ".gitignore").read_text())

    def test_update_without_source_or_stamp_fails_clearly(self):
        install(self.proj)
        (self.proj / "plans/.sam-version").unlink()
        env_backup = GIT_ENV.pop("SAM_TEMPLATE_PATH", None)
        try:
            r = update(self.proj, check=False)
        finally:
            if env_backup is not None:
                GIT_ENV["SAM_TEMPLATE_PATH"] = env_backup
        self.assertEqual(r.returncode, 1)
        self.assertIn("no SAM source found", r.stderr)


class FreshClone(ProjectCase):
    def test_clone_then_install_starts_a_new_build(self):
        install(self.proj)
        state = self.proj / "plans/state.json"
        state.write_text(json.dumps({"next_action_id": "Staff.DraftQuestions"}))
        (self.proj / "plans/BUILD.md").write_text("# real build\n")
        self.commit_all()
        clone = self.tmp / "clone"
        git(self.tmp, "clone", "-q", str(self.proj), str(clone))
        self.assertEqual(sorted(p.name for p in (clone / "plans").iterdir()),
                         sorted(Path(p).name for p in SEVEN))
        self.assertFalse((clone / "CLAUDE.md").exists())
        install(clone)
        self.assertEqual((clone / "plans/BUILD.md").read_text(), "# real build\n")
        fresh = json.loads((clone / "plans/state.json").read_text(encoding="utf-8"))
        self.assertEqual(fresh["next_action_id"], "Product.ProductVision")
        self.assertEqual(git(clone, "status", "--porcelain"), "")


class ManifestInventory(unittest.TestCase):
    def test_every_template_file_is_in_the_manifest(self):
        manifest = json.loads((REPO / "plans/sync-manifest.json").read_text(encoding="utf-8"))
        sources = {e["source"] for e in manifest["files"] if e.get("source")}
        tracked_plans = {p for p in git(REPO, "ls-files", "plans").splitlines() if p}
        self.assertEqual(tracked_plans - sources, set())

    def test_exactly_seven_tracked_plans(self):
        manifest = json.loads((REPO / "plans/sync-manifest.json").read_text(encoding="utf-8"))
        kept = sorted(e["target"] for e in manifest["files"] if not e["gitignore"])
        self.assertEqual(kept, SEVEN)


@unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell not available")
class CommitHelper(ProjectCase):
    def test_nothing_to_commit_is_success(self):
        install(self.proj)
        self.commit_all()
        (self.proj / "plans/thread.md").write_text("only ignored runtime files changed\n")
        ps = shutil.which("pwsh") or shutil.which("powershell")
        r = sh([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                str(self.proj / "plans/commit.ps1")], self.proj, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Nothing to commit", r.stdout)


def setUpModule() -> None:
    global LEGACY_REF
    tags = git(REPO, "log", "--format=%H", "-1", "--grep=^v1.8.0").strip()
    LEGACY_REF = tags or "missing-legacy-ref"


if __name__ == "__main__":
    unittest.main()
