#!/usr/bin/env python3
"""
OSHWA Hardware Repository Validator
Audits open-source hardware repositories for compliance with Open Source Hardware
Association (OSHWA) criteria and maker-friendly release standards.
"""

import sys
import os
import csv
import argparse
from pathlib import Path

# Required BOM columns according to open hardware standards
REQUIRED_BOM_HEADERS = [
    "Part Number",
    "Component Name",
    "Material / Spec",
    "Qty",
    "Category",
    "Vendor / Standard Reference",
    "Estimated Unit Cost (USD)",
]

RECOMMENDED_BOM_HEADERS = [
    "Sourcing Notes"
]

def check_file_exists(repo_path: Path, relative_path: str, description: str, critical: bool = True):
    full_path = repo_path / relative_path
    exists = full_path.exists()
    status = "PASS" if exists else ("FAIL" if critical else "WARN")
    size_info = f"({full_path.stat().st_size} bytes)" if exists else "(missing)"
    print(f"  [{status}] {description:.<36} {relative_path} {size_info}")
    return exists

def validate_bom(repo_path: Path):
    bom_file = repo_path / "bom" / "bom.csv"
    if not bom_file.exists():
        print("  [FAIL] BOM file does not exist at bom/bom.csv")
        return False, 0, 0.0

    print(f"\n--- Checking Bill of Materials ({bom_file.relative_to(repo_path)}) ---")
    try:
        with open(bom_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                print("  [FAIL] BOM file is completely empty.")
                return False, 0, 0.0

            # Clean headers
            header = [h.strip() for h in header]

            missing_headers = [h for h in REQUIRED_BOM_HEADERS if h not in header]
            if missing_headers:
                print(f"  [FAIL] Missing required BOM columns: {', '.join(missing_headers)}")
                return False, 0, 0.0
            print(f"  [PASS] All {len(REQUIRED_BOM_HEADERS)} required columns present in header.")

            row_count = 0
            total_cost = 0.0
            part_col = header.index("Part Number")
            name_col = header.index("Component Name")
            qty_col = header.index("Qty")
            cost_col = header.index("Estimated Unit Cost (USD)")

            for row_idx, row in enumerate(reader, start=2):
                if not row or not any(row):
                    continue
                row_count += 1
                part_no = row[part_col].strip() if len(row) > part_col else ""
                part_name = row[name_col].strip() if len(row) > name_col else ""
                qty_str = row[qty_col].strip() if len(row) > qty_col else "0"
                cost_str = row[cost_col].strip() if len(row) > cost_col else "0.0"

                if not part_no:
                    print(f"  [WARN] Row {row_idx}: Empty Part Number for '{part_name}'")

                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = 1

                try:
                    unit_cost = float(cost_str.replace("$", "").strip())
                except ValueError:
                    unit_cost = 0.0

                total_cost += (qty * unit_cost)

            print(f"  [PASS] Successfully parsed {row_count} components.")
            print(f"  [INFO] Estimated Total BOM Cost: ${total_cost:.2f} USD")
            return True, row_count, total_cost
    except Exception as e:
        print(f"  [FAIL] Error reading BOM: {e}")
        return False, 0, 0.0

def validate_cad_structure(repo_path: Path):
    print(f"\n--- Checking CAD / Design Source Structure ---")
    cad_dir = repo_path / "cad"
    if not cad_dir.exists():
        print("  [FAIL] 'cad/' directory is missing.")
        return False

    subdirs = ["parts", "assemblies", "exports"]
    all_ok = True
    for sub in subdirs:
        sub_path = cad_dir / sub
        exists = sub_path.exists() and sub_path.is_dir()
        status = "PASS" if exists else "WARN"
        print(f"  [{status}] Subdirectory cad/{sub:<15} {'Found' if exists else 'Not found'}")
        if not exists:
            all_ok = False
    return True

def validate_licenses(repo_path: Path):
    print(f"\n--- Checking Open Hardware Licensing ---")
    hw_license = check_file_exists(repo_path, "LICENSE-HARDWARE", "Hardware License (CERN-OHL)", critical=True)
    doc_license = check_file_exists(repo_path, "LICENSE-DOCS", "Docs License (CC-BY-4.0)", critical=True)
    return hw_license and doc_license

def validate_documentation(repo_path: Path):
    print(f"\n--- Checking Documentation & Assembly Guides ---")
    readme_ok = check_file_exists(repo_path, "README.md", "Project README", critical=True)
    oshwa_ok = check_file_exists(repo_path, "OSHWA.md", "OSHWA Compliance Checklist", critical=True)
    assembly_ok = check_file_exists(repo_path, "docs/assembly-guide.md", "Step-by-Step Assembly Guide", critical=True)
    gitignore_ok = check_file_exists(repo_path, ".gitignore", "Git Ignore File", critical=False)
    return readme_ok and oshwa_ok and assembly_ok

def main():
    parser = argparse.ArgumentParser(description="Audit an open-source hardware project repository for OSHWA compliance.")
    parser.add_argument("--repo", default=".", help="Path to hardware repository root (default: current directory)")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    print("=" * 65)
    print(f"   OSHWA & Open-Source Hardware Repository Auditor")
    print(f"   Target: {repo_path}")
    print("=" * 65)

    licenses_pass = validate_licenses(repo_path)
    docs_pass = validate_documentation(repo_path)
    cad_pass = validate_cad_structure(repo_path)
    bom_pass, total_parts, total_cost = validate_bom(repo_path)

    print("\n" + "=" * 65)
    print("               AUDIT SUMMARY RESULTS")
    print("=" * 65)
    print(f"  * Licensing Verification      : {'PASS' if licenses_pass else 'FAIL'}")
    print(f"  * Documentation & Guide       : {'PASS' if docs_pass else 'FAIL'}")
    print(f"  * CAD Directory Structure     : {'PASS' if cad_pass else 'WARN'}")
    print(f"  * Bill of Materials (BOM)     : {'PASS' if bom_pass else 'FAIL'} ({total_parts} parts, ${total_cost:.2f} USD)")

    all_passed = licenses_pass and docs_pass and bom_pass

    print("-" * 65)
    if all_passed:
        print("  RESULT: REPOSITORY PASSES OSHWA & OPEN HARDWARE STANDARDS")
        print("  The project is fully structured for open maker reproducibility!")
        print("=" * 65)
        sys.exit(0)
    else:
        print("  RESULT: COMPLIANCE ISSUES DETECTED")
        print("  Please resolve the FAIL items listed above.")
        print("=" * 65)
        sys.exit(1)

if __name__ == "__main__":
    main()
