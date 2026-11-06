"""Gemeinsame Helfer für die Browser-Tests."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / "Unterlagen-Sortierer"
APP = (PROG / "Unterlagen-Sortierer.html").as_uri()
DOCS_DIR = ROOT / "tests" / "testdocs"
DOCS = sorted([str(p) for p in DOCS_DIR.glob("*.pdf")] + [str(p) for p in DOCS_DIR.glob("*.jpg")])

class Pruefer:
    def __init__(self, name):
        self.name, self.ok, self.bad = name, 0, 0
        print(f"== {name}")
    def check(self, desc, cond, extra=""):
        if cond: self.ok += 1
        else:
            self.bad += 1; print("  ✗", desc, extra)
    def ende(self):
        print(f"   {self.name}: {self.ok} bestanden, {self.bad} fehlgeschlagen")
        sys.exit(1 if self.bad else 0)
