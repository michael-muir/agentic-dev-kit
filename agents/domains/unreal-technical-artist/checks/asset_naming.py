#!/usr/bin/env python3
"""Check Unreal asset file names: a known type prefix, no spaces, ASCII only.

Works from file names alone (fine with Git LFS pointers). Assets under Content/Developers/
and Content/Collections/ are skipped. Extend the prefix list with the ALLOWED_PREFIXES
environment variable, e.g. ALLOWED_PREFIXES="DA_,DT_,CUR_".
Exit code 1 if any violations were found.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import PurePosixPath

PREFIXES = {
    # blueprints & gameplay
    "BP_", "BPI_", "BPFL_", "BPML_", "ABP_", "WBP_", "GA_", "GE_", "GC_", "BT_", "BB_", "AI_",
    "E_", "F_", "S_", "DA_", "DT_", "CT_", "CUR_", "ST_", "IA_", "IMC_",
    # materials & textures
    "M_", "MI_", "MF_", "MPC_", "PP_", "T_", "TC_", "RT_", "LUT_", "SP_",
    # meshes & animation
    "SM_", "SK_", "SKM_", "SKEL_", "PHYS_", "PHYS", "A_", "AM_", "AS_", "BS_", "AO_", "CR_", "IK_", "RTG_",
    # fx, audio, levels, misc
    "NS_", "NE_", "NMS_", "PS_", "SC_", "SW_", "MS_", "SA_", "ATT_", "L_", "LV_", "MAP_", "LS_",
    "SEQ_", "PCG_", "HLOD_", "FT_", "Font_", "UI_",
}
SKIP_DIRS = ("Content/Developers/", "Content/Collections/")


def asset_files() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout
        names = out.splitlines()
    except (OSError, subprocess.CalledProcessError):
        names = [os.path.relpath(os.path.join(d, f)).replace("\\", "/")
                 for d, _, fs in os.walk(".") for f in fs]
    return [n for n in names if n.endswith((".uasset", ".umap"))
            and not any(s in n for s in SKIP_DIRS)]


def main() -> int:
    extra = {p.strip() for p in os.environ.get("ALLOWED_PREFIXES", "").split(",") if p.strip()}
    prefixes = PREFIXES | extra
    problems = []
    for path in asset_files():
        stem = PurePosixPath(path).stem
        if " " in path:
            problems.append(f"{path}: path contains spaces")
        if not path.isascii():
            problems.append(f"{path}: path contains non-ASCII characters")
        if not any(stem.startswith(p) for p in prefixes):
            problems.append(f"{path}: '{stem}' has no known asset-type prefix (e.g. BP_, M_, T_, SM_)")
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} asset naming problem(s). Add project prefixes with ALLOWED_PREFIXES.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
