#!/usr/bin/env python3
"""Second acquisition wave for T3.

Extends the verified base collector with additional Perekrestok Yandex business IDs
observed in the public Perekrestok/Yandex review contour. The base collector still
validates that every business resolves to Perekrestok before accepting reviews.
"""

from __future__ import annotations

import sys

import acquire_perekrestok_public as base

# Additional business IDs observed on public Perekrestok/Yandex review pages.
# No row is accepted solely because an ID is listed here: base.extract_maps_store()
# rejects a business when its resolved name is not Perekrestok/Perekryostok.
ADDITIONAL_STORES = [
    ("158894039840", "Перекрёсток / Yandex business 158894039840"),
    ("171071481416", "Перекрёсток / Yandex business 171071481416"),
    ("207411958069", "Перекрёсток / Yandex business 207411958069"),
    ("1033635077", "Перекрёсток / Yandex business 1033635077"),
    ("89580496666", "Перекрёсток / Yandex business 89580496666"),
    ("14309395134", "Перекрёсток / Yandex business 14309395134"),
    ("122713806381", "Перекрёсток / Yandex business 122713806381"),
    ("89505138118", "Перекрёсток / Yandex business 89505138118"),
    ("208592166351", "Перекрёсток / Yandex business 208592166351"),
    ("73117390093", "Перекрёсток / Yandex business 73117390093"),
    ("59062427580", "Перекрёсток / Yandex business 59062427580"),
    ("241633336363", "Перекрёсток / Yandex business 241633336363"),
    ("63715298452", "Перекрёсток / Yandex business 63715298452"),
    ("199671455065", "Перекрёсток / Yandex business 199671455065"),
    ("212916785236", "Перекрёсток / Yandex business 212916785236"),
    ("100264989344", "Сочи/Адлер, Перекрёсток / Yandex business 100264989344"),
    ("155093500740", "Москва, Балаклавский проспект, 5А"),
]

existing = {business_id for business_id, _ in base.MAP_STORES}
base.MAP_STORES.extend((business_id, label) for business_id, label in ADDITIONAL_STORES if business_id not in existing)

if __name__ == "__main__":
    sys.exit(base.main())
