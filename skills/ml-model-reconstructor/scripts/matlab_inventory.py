#!/usr/bin/env python3
"""Create a lightweight inventory of MATLAB code for model reconstruction.

This script intentionally avoids full MATLAB parsing. It gives Claude Code a
fast static map of files, functions, assignments, solver calls, DSP calls, and
potential model/derivation clues before manual inspection.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

MATLAB_EXTS = {".m", ".mlx", ".slx", ".mdl"}
DSP_CALLS = {
    "fft", "ifft", "fftshift", "ifftshift", "filter", "filtfilt", "conv",
    "xcorr", "xcov", "pwelch", "periodogram", "spectrogram", "stft", "cwt",
    "butter", "cheby1", "cheby2", "ellip", "fir1", "fir2", "designfilt",
    "freqz", "zplane", "hilbert", "resample", "decimate", "interp", "downsample",
    "upsample", "awgn", "snr", "pspectrum",
}
OPT_CALLS = {
    "fmincon", "fminunc", "quadprog", "linprog", "lsqnonlin", "lsqcurvefit",
    "fsolve", "fzero", "ga", "particleswarm", "patternsearch", "simulannealbnd",
    "intlinprog", "optimproblem", "optimvar", "solve", "lsqlin",
}
LINEAR_ALG_CALLS = {
    "eig", "svd", "qr", "chol", "pinv", "inv", "rank", "norm", "kron",
    "diag", "trace", "null", "orth", "mldivide", "mrdivide",
}

FUNCTION_RE = re.compile(
    r"^\s*function\s+(?:(?P<outputs>\[[^\]]+\]|\w+)\s*=\s*)?(?P<name>[A-Za-z]\w*)\s*\((?P<inputs>[^)]*)\)",
    re.MULTILINE,
)
ASSIGN_RE = re.compile(r"^\s*(?P<lhs>[A-Za-z]\w*(?:\s*\([^=;]*\))?)\s*=\s*(?P<rhs>[^;%\n]+)", re.MULTILINE)
CALL_RE = re.compile(r"(?<![\w.])(?P<name>[A-Za-z]\w*)\s*\(")
LOOP_RE = re.compile(r"^\s*(for|while)\b(?P<body>.*)$", re.MULTILINE)
BRANCH_RE = re.compile(r"^\s*(if|elseif|switch)\b(?P<body>.*)$", re.MULTILINE)
COMMENT_RE = re.compile(r"^\s*%+(?P<text>.*)$", re.MULTILINE)


@dataclass
class MatlabFunction:
    name: str
    inputs: list[str]
    outputs: list[str]
    line: int


@dataclass
class MatlabFileInventory:
    path: str
    kind: str
    line_count: int
    functions: list[MatlabFunction]
    top_assignments: list[dict]
    calls: dict[str, int]
    dsp_calls: dict[str, int]
    optimization_calls: dict[str, int]
    linear_algebra_calls: dict[str, int]
    loops: list[dict]
    branches: list[dict]
    comments_preview: list[str]
    likely_roles: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def split_csvish(s: str) -> list[str]:
    s = s.strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [p.strip() for p in s.split(",") if p.strip()]


def count_calls(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in CALL_RE.finditer(text):
        name = match.group("name")
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def extract_functions(text: str) -> list[MatlabFunction]:
    out: list[MatlabFunction] = []
    for match in FUNCTION_RE.finditer(text):
        outputs = split_csvish(match.group("outputs") or "")
        inputs = split_csvish(match.group("inputs") or "")
        out.append(MatlabFunction(match.group("name"), inputs, outputs, line_number(text, match.start())))
    return out


def extract_assignments(text: str, max_items: int) -> list[dict]:
    items: list[dict] = []
    for match in ASSIGN_RE.finditer(text):
        lhs = re.sub(r"\s+", "", match.group("lhs"))
        rhs = match.group("rhs").strip()
        if len(rhs) > 160:
            rhs = rhs[:157] + "..."
        items.append({"line": line_number(text, match.start()), "lhs": lhs, "rhs_preview": rhs})
        if len(items) >= max_items:
            break
    return items


def extract_statements(text: str, regex: re.Pattern[str], max_items: int) -> list[dict]:
    items: list[dict] = []
    for match in regex.finditer(text):
        body = re.sub(r"\s+", " ", match.group(0).strip())
        if len(body) > 160:
            body = body[:157] + "..."
        items.append({"line": line_number(text, match.start()), "statement": body})
        if len(items) >= max_items:
            break
    return items


def comments_preview(text: str, max_items: int) -> list[str]:
    comments: list[str] = []
    for match in COMMENT_RE.finditer(text):
        c = match.group("text").strip()
        if c:
            comments.append(c[:180])
        if len(comments) >= max_items:
            break
    return comments


def infer_roles(path: Path, calls: dict[str, int], functions: list[MatlabFunction], text: str) -> list[str]:
    roles: list[str] = []
    name = path.name.lower()
    lower = text.lower()
    if any(c in calls for c in DSP_CALLS):
        roles.append("signal_processing")
    if any(c in calls for c in OPT_CALLS):
        roles.append("optimization")
    if any(c in calls for c in LINEAR_ALG_CALLS) or "\\" in text:
        roles.append("linear_algebra_or_least_squares")
    if any(token in lower for token in ["objective", "cost", "loss", "residual", "constraint", "gradient"]):
        roles.append("model_objective_or_constraints")
    if any(token in name for token in ["main", "run", "demo", "test"]):
        roles.append("possible_entry_point")
    if not functions and path.suffix == ".m":
        roles.append("script")
    if functions:
        roles.append("function_file")
    if path.suffix in {".slx", ".mdl"}:
        roles.append("simulink_model")
    return roles


def inventory_file(path: Path, root: Path, max_items: int) -> MatlabFileInventory:
    if path.suffix in {".slx", ".mlx"}:
        # These may be binary/zip-based. Do not attempt to parse as plain text.
        return MatlabFileInventory(
            path=str(path.relative_to(root)),
            kind=path.suffix.lstrip("."),
            line_count=0,
            functions=[],
            top_assignments=[],
            calls={},
            dsp_calls={},
            optimization_calls={},
            linear_algebra_calls={},
            loops=[],
            branches=[],
            comments_preview=[],
            likely_roles=["live_script_or_simulink_needs_matlab_metadata"],
        )

    text = read_text(path)
    calls = count_calls(text)
    functions = extract_functions(text)
    roles = infer_roles(path, calls, functions, text)
    return MatlabFileInventory(
        path=str(path.relative_to(root)),
        kind=path.suffix.lstrip("."),
        line_count=text.count("\n") + 1,
        functions=functions,
        top_assignments=extract_assignments(text, max_items),
        calls=dict(list(calls.items())[:max_items]),
        dsp_calls={k: calls[k] for k in sorted(DSP_CALLS) if k in calls},
        optimization_calls={k: calls[k] for k in sorted(OPT_CALLS) if k in calls},
        linear_algebra_calls={k: calls[k] for k in sorted(LINEAR_ALG_CALLS) if k in calls},
        loops=extract_statements(text, LOOP_RE, max_items),
        branches=extract_statements(text, BRANCH_RE, max_items),
        comments_preview=comments_preview(text, max_items),
        likely_roles=roles,
    )


def iter_matlab_files(paths: Iterable[Path]) -> tuple[Path, list[Path]]:
    all_files: list[Path] = []
    roots = [p.resolve() for p in paths]
    root = roots[0] if len(roots) == 1 else Path.cwd().resolve()
    for p in roots:
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file() and child.suffix.lower() in MATLAB_EXTS:
                    all_files.append(child)
        elif p.is_file() and p.suffix.lower() in MATLAB_EXTS:
            all_files.append(p)
    return root, sorted(set(all_files))


def summarize(files: list[MatlabFileInventory]) -> dict:
    role_counts: dict[str, int] = {}
    for f in files:
        for r in f.likely_roles:
            role_counts[r] = role_counts.get(r, 0) + 1
    entry_candidates = [f.path for f in files if "possible_entry_point" in f.likely_roles]
    if not entry_candidates:
        scripts = [f.path for f in files if "script" in f.likely_roles]
        entry_candidates = scripts[:10]
    return {
        "file_count": len(files),
        "role_counts": dict(sorted(role_counts.items())),
        "entry_candidates": entry_candidates[:20],
        "has_signal_processing": any(f.dsp_calls for f in files),
        "has_optimization": any(f.optimization_calls for f in files),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory MATLAB files for model reconstruction")
    parser.add_argument("paths", nargs="+", help="MATLAB file(s) or project folder(s)")
    parser.add_argument("--output", "-o", help="Write JSON output to this path")
    parser.add_argument("--max-items", type=int, default=40, help="Maximum items per section per file")
    args = parser.parse_args()

    input_paths = [Path(p) for p in args.paths]
    root, paths = iter_matlab_files(input_paths)
    files = [inventory_file(p, root, args.max_items) for p in paths]
    payload = {
        "root": str(root),
        "summary": summarize(files),
        "files": [asdict(f) for f in files],
        "notes": [
            "This is a regex-based inventory, not a complete MATLAB parser.",
            "Use it to prioritize manual inspection and derive evidence-backed equations.",
        ],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
