import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = ROOT / "0_main.clp"
OUTPUT_DIR = ROOT / "tests" / "output"


@dataclass
class TestCase:
    name: str
    answers: list[str]
    must_contain: list[str]
    must_not_contain: list[str]


COMMON_MUST_NOT = [
    "NO DESTINATIONS FOUND",
    "Slot 'month' does not exist",
    "[PRCCODE4]",
]


TEST_CASES = [
    TestCase(
        name="near_adventure_cold_city",
        answers=[
            "1200",  # budget
            "8",  # month
            "12",  # duration
            "1",  # flexibility NONE
            "7",  # continent ANY
            "1",  # distance NEAR
            "1",  # trip ADVENTURE
            "5",  # climate COLD
            "3",  # temperature COLD
            "n",  # beach
            "y",  # mountain
            "y",  # nature
            "2",  # population CITY
            "y",  # culture
            "n",  # party
            "y",  # activities
            "y",  # history
            "n",  # offers filter
        ],
        must_contain=[
            "TOP 5 DESTINATION RECOMMENDATIONS",
            "Distance preference: NEAR",
            "Climate: COLD | Temperature: COLD",
            "Destination type: CITY",
        ],
        must_not_contain=COMMON_MUST_NOT,
    ),
    TestCase(
        name="culture_beach_with_offers_filter",
        answers=[
            "1200",
            "3",
            "19",
            "3",  # flexibility HIGH
            "7",
            "3",  # distance ANY
            "4",  # trip ROMANTIC
            "6",  # climate ANY
            "4",  # temperature ANY
            "y",
            "n",
            "n",
            "4",  # population ANY
            "y",
            "n",
            "n",
            "n",
            "y",  # offers filter enabled
            "2500",  # max offer price
            "",  # offer duration any
        ],
        must_contain=[
            "Offers filter created.",
            "Flexibility: HIGH",
            "TOP 5 DESTINATION RECOMMENDATIONS",
        ],
        must_not_contain=COMMON_MUST_NOT,
    ),
    TestCase(
        name="continent_preference_europe",
        answers=[
            "1800",
            "10",
            "7",
            "2",  # flexibility LOW
            "1",  # continent Europe
            "3",  # distance ANY
            "3",  # trip CULTURAL
            "6",
            "4",
            "n",
            "n",
            "n",
            "1",  # major-city
            "y",
            "n",
            "n",
            "y",
            "n",
        ],
        must_contain=[
            "Preferred continent: Europe | Distance preference: ANY",
            "Destination type: MAJOR-CITY",
            "TOP 5 DESTINATION RECOMMENDATIONS",
        ],
        must_not_contain=COMMON_MUST_NOT,
    ),
    TestCase(
        name="far_preference_relaxation",
        answers=[
            "2200",
            "5",
            "10",
            "1",
            "7",
            "2",  # FAR
            "2",  # RELAXATION
            "3",  # TROPICAL
            "1",  # HOT
            "y",
            "n",
            "y",
            "4",
            "n",
            "n",
            "y",
            "n",
            "n",
        ],
        must_contain=[
            "Distance preference: FAR",
            "Trip type: RELAXATION",
            "TOP 5 DESTINATION RECOMMENDATIONS",
        ],
        must_not_contain=COMMON_MUST_NOT,
    ),
]


def run_case(case: TestCase) -> tuple[bool, str, str]:
    payload = "\n".join(case.answers) + "\n"
    proc = subprocess.run(
        ["clips", "-f2", str(MAIN_FILE)],
        input=payload,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=90,
    )
    output = proc.stdout + "\n" + proc.stderr

    if proc.returncode != 0:
        return False, f"process exited with {proc.returncode}\n{output[:1200]}", output

    for needle in case.must_contain:
        if needle not in output:
            return False, f"missing expected text: {needle}", output

    for forbidden in case.must_not_contain:
        if forbidden in output:
            return False, f"forbidden text found: {forbidden}", output

    if not re.search(r"Total:\s+\d+\s+destinations", output):
        return False, "summary total not found", output

    return True, "ok", output


def main() -> int:
    print("Running CLIPS smoke suite...\n")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    for case in TEST_CASES:
        ok, detail, output = run_case(case)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case.name} - {detail}")
        out_file = OUTPUT_DIR / f"{case.name}.out.txt"
        out_file.write_text(output, encoding="utf-8")
        if not ok:
            failures.append((case.name, detail))

    print(f"\nSaved outputs to: {OUTPUT_DIR}")
    print(f"\nResult: {len(TEST_CASES) - len(failures)}/{len(TEST_CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
