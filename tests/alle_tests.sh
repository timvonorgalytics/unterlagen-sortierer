#!/usr/bin/env bash
# Führt alle Browser-Tests aus. Voraussetzung (einmalig):
#   python3 -m pip install playwright && python3 -m playwright install chromium
cd "$(dirname "$0")" || exit 1
fail=0
for t in test_namen.py test_regeln.py test_dateimodus.py test_teilen.py test_drehen.py test_ordnermodus.py test_mehrkunden.py test_offline.py test_ci.py; do
  python3 "$t" || fail=1
done
echo
[ $fail -eq 0 ] && echo "ALLE TESTS BESTANDEN" || echo "MINDESTENS EIN TEST FEHLGESCHLAGEN"
exit $fail
