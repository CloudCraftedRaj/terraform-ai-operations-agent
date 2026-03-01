import os
import shlex
import subprocess
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("terraform")

# -------------------------------------------------------------------
# Repo layout expectation:
# <repo>/
#   mcp-server/terraform_mcp.py
#   examples/azure-terraform-project/terraform/  <-- terraform root
# -------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEFAULT_TF_ROOT = REPO_ROOT / "examples" / "azure-terraform-project" / "terraform"

# Allow only these Terraform subcommands (safety)
ALLOWED_SUBCOMMANDS = {
    "version",
    "init",
    "validate",
    "plan",
    "show",
    "apply",
    "destroy",
    "workspace",
}

def find_terraform_root(start: Path) -> Path:
    """
    Find a Terraform root folder by walking up and looking for a strong signal.
    """
    candidates = ["providers.tf", ".terraform.lock.hcl", "main.tf"]
    cur = start.resolve()

    # Walk up a few levels to find terraform files
    for _ in range(6):
        if any((cur / name).exists() for name in candidates):
            return cur
        cur = cur.parent

    # Fallback to default expected path
    return DEFAULT_TF_ROOT.resolve()

def get_tf_workdir() -> Path:
    """
    Determine TF working directory.
    Priority:
      1) TF_WORKDIR env var
      2) infer from expected repo structure
    """
    env = os.environ.get("TF_WORKDIR", "").strip()
    if env:
        p = Path(env).expanduser()
        return p.resolve() if p.is_absolute() else (REPO_ROOT / p).resolve()

    return DEFAULT_TF_ROOT.resolve()

TF_WORKDIR = find_terraform_root(get_tf_workdir())

def ensure_allowed_terraform(cmd_list: list[str]) -> None:
    """
    Allow: terraform [global flags] <subcommand> ...
    Example: terraform -chdir=/x plan -input=false
    """
    if not cmd_list or cmd_list[0] != "terraform":
        raise ValueError("Only terraform commands are allowed.")

    # Find the first non-flag token after 'terraform' — that's the subcommand.
    subcmd = None
    for tok in cmd_list[1:]:
        if tok.startswith("-"):
            continue
        subcmd = tok
        break

    if subcmd is None:
        raise ValueError("Terraform subcommand not found.")

    if subcmd not in ALLOWED_SUBCOMMANDS:
        raise ValueError(f"Command not allowed: terraform {subcmd}")

def run_terraform(args: list[str], timeout: int = 3600) -> str:
    """
    Run terraform using -chdir to guarantee execution from TF_WORKDIR.
    """
    cmd = ["terraform", f"-chdir={str(TF_WORKDIR)}"] + args

    # Safety gate
    ensure_allowed_terraform(cmd)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "TF_IN_AUTOMATION": "1"},
    )

    out = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    return f"[tf_root={TF_WORKDIR}]\n$ {' '.join(shlex.quote(x) for x in cmd)}\n\n{out}"

# ------------------ MCP Tools ------------------

@mcp.tool()
def tf_where() -> str:
    """Show which Terraform directory this MCP server is using."""
    return f"Terraform working directory:\n{TF_WORKDIR}"

@mcp.tool()
def tf_version() -> str:
    return run_terraform(["version"])

@mcp.tool()
def tf_init(reconfigure: bool = False, upgrade: bool = False) -> str:
    args = ["init", "-input=false"]
    if reconfigure:
        args.append("-reconfigure")
    if upgrade:
        args.append("-upgrade")
    return run_terraform(args, timeout=3600)

@mcp.tool()
def tf_validate() -> str:
    return run_terraform(["validate"])

@mcp.tool()
def tf_plan(var_file: str = "", out_file: str = "tfplan") -> str:
    args = ["plan", "-input=false", f"-out={out_file}"]
    if var_file:
        vf = Path(var_file).expanduser()
        if not vf.is_absolute():
            # Allow paths relative to repo root
            vf = (REPO_ROOT / vf).resolve()
        args.append(f"-var-file={str(vf)}")
    return run_terraform(args, timeout=3600)

@mcp.tool()
def tf_show_plan(plan_file: str = "tfplan") -> str:
    return run_terraform(["show", "-no-color", plan_file])

@mcp.tool()
def tf_apply(plan_file: str = "tfplan", auto_approve: bool = False) -> str:
    args = ["apply", "-input=false"]
    if auto_approve:
        args.append("-auto-approve")
    args.append(plan_file)
    return run_terraform(args, timeout=3600)

@mcp.tool()
def tf_destroy(var_file: str = "", auto_approve: bool = False) -> str:
    args = ["destroy", "-input=false"]
    if var_file:
        vf = Path(var_file).expanduser()
        if not vf.is_absolute():
            vf = (REPO_ROOT / vf).resolve()
        args.append(f"-var-file={str(vf)}")
    if auto_approve:
        args.append("-auto-approve")
    return run_terraform(args, timeout=3600)

@mcp.tool()
def tf_workspace_list() -> str:
    return run_terraform(["workspace", "list"])

@mcp.tool()
def tf_workspace_select(name: str) -> str:
    return run_terraform(["workspace", "select", name])

@mcp.tool()
def tf_workspace_new(name: str) -> str:
    return run_terraform(["workspace", "new", name])

@mcp.tool()
def tf_plan_destroy(var_file: str = "") -> str:
    """
    Preview what Terraform will destroy WITHOUT deleting resources.
    """
    args = ["plan", "-destroy", "-input=false"]
    if var_file:
        vf = Path(var_file).expanduser()
        if not vf.is_absolute():
            vf = (REPO_ROOT / vf).resolve()
        args.append(f"-var-file={str(vf)}")
    return run_terraform(args, timeout=3600)

if __name__ == "__main__":
    if not TF_WORKDIR.exists():
        raise SystemExit(f"Terraform directory not found: {TF_WORKDIR}")
    mcp.run()
    