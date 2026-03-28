import asyncio
import json

from .config import settings


class FocusRelayError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def build_args(flags: set[str] | None = None, **kwargs) -> list[str]:
    """Convert keyword arguments to CLI flags.

    - None values are skipped
    - Names in `flags` set are treated as presence-only (@Flag): included only when True
    - Other bools are passed as --key true/false (@Option)
    - Everything else is --key value with underscore→hyphen conversion
    """
    flags = flags or set()
    args: list[str] = []
    for key, value in kwargs.items():
        if value is None:
            continue
        flag_name = f"--{key.replace('_', '-')}"
        if key in flags:
            if value:
                args.append(flag_name)
        elif isinstance(value, bool):
            args.extend([flag_name, str(value).lower()])
        else:
            args.extend([flag_name, str(value)])
    return args


async def run_focusrelay(subcommand: str, args: list[str] | None = None) -> dict | list:
    cmd = [settings.focusrelay_bin, subcommand] + (args or [])
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FocusRelayError(
            f"focusrelay binary not found at: {settings.focusrelay_bin}",
            status_code=503,
        )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=settings.command_timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise FocusRelayError("Command timed out", status_code=504)

    if proc.returncode != 0:
        error_msg = stderr.decode().strip() or f"CLI exited with code {proc.returncode}"
        raise FocusRelayError(error_msg)

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise FocusRelayError(f"Invalid JSON from CLI: {e}")
