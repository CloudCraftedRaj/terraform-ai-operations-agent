import os
import shlex
import subprocess
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("terraform")

ALLOWED_COMMANDS = [
    "terraform init",
    "terraform plan",
    "terraform apply",
]

# Use env var if provided; fallback to this file's directory
TF_WORKDIR = Path(os.environ.get("TF_WORKDIR", Path(__file__).resolve().parent)).resolve()

def run(cmd: str, timeout: int = 3600) -> str:
    """
    Run a command in TF_WORKDIR and return combined stdout/stderr.
    """
    proc = subprocess.run(
        shlex.split(cmd),
        cwd=str(TF_WORKDIR),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "TF_IN_AUTOMATION": "1"},
    )
    out = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    return f"[cwd={TF_WORKDIR}]\n$ {cmd}\n\n{out}"

@mcp.tool()
def tf_version() -> str:
    return run("terraform version")

@mcp.tool()
def tf_init(reconfigure: bool = False, upgrade: bool = False) -> str:
    args = ["terraform", "init", "-input=false"]
    if reconfigure:
        args.append("-reconfigure")
    if upgrade:
        args.append("-upgrade")
    return run(" ".join(args), timeout=3600)

@mcp.tool()
def tf_validate() -> str:
    return run("terraform validate")

@mcp.tool()
def tf_plan(var_file: str = "", out_file: str = "tfplan") -> str:
    args = ["terraform", "plan", "-input=false", f"-out={out_file}"]
    if var_file:
        # expects a file path relative to TF_WORKDIR or absolute
        args.append(f"-var-file={var_file}")
    return run(" ".join(args), timeout=3600)

@mcp.tool()
def tf_show_plan(plan_file: str = "tfplan") -> str:
    return run(f"terraform show -no-color {plan_file}")

@mcp.tool()
def tf_apply(plan_file: str = "tfplan", auto_approve: bool = False) -> str:
    # Safety: default is NOT auto-approve. You can review plan before applying.
    if auto_approve:
        return run(f"terraform apply -input=false -auto-approve {plan_file}", timeout=3600)
    return run(f"terraform apply -input=false {plan_file}", timeout=3600)

@mcp.tool()
def tf_destroy(var_file: str = "", auto_approve: bool = False) -> str:
    args = ["terraform", "destroy", "-input=false"]
    if var_file:
        args.append(f"-var-file={var_file}")
    if auto_approve:
        args.append("-auto-approve")
    return run(" ".join(args), timeout=3600)

@mcp.tool()
def tf_workspace_list() -> str:
    return run("terraform workspace list")

@mcp.tool()
def tf_workspace_select(name: str) -> str:
    return run(f"terraform workspace select {shlex.quote(name)}")

@mcp.tool()
def tf_workspace_new(name: str) -> str:
    return run(f"terraform workspace new {shlex.quote(name)}")

@mcp.tool()
def tf_plan_destroy(var_file: str = "") -> str:
    """
    Preview what Terraform will destroy WITHOUT deleting resources.
    """

    cmd = ["terraform", "plan", "-destroy", "-input=false"]

    if var_file:
        cmd.append(f"-var-file={var_file}")

    return run(" ".join(cmd))

if __name__ == "__main__":
    # Make sure directory exists
    if not TF_WORKDIR.exists():
        raise SystemExit(f"TF_WORKDIR does not exist: {TF_WORKDIR}")
    mcp.run()