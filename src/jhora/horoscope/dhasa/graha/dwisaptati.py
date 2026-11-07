#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
"""
Alias module for Dwisatpathi (=72) Dasha-bhukthi-antara-sukshma-prana.

'Dwisaptati' is the correct Sanskrit name for this dhasa system (confirmed
directly from JHora's own UI label: "Dwi-saptati sama dasa" -- dwi+saptati
= "seventy-two", sama = "equal"). The internal module/file is named
`dwisatpathi.py` (matching the existing codebase's naming, including
`dwisatpathi_immediate_children`, `human_life_span_for_dwisatpathi_dhasa`,
and `pvr_tests.dwisatpathi_test()`), so that name was kept as the CANONICAL
implementation to avoid breaking any existing internal references.

This module is a thin, zero-logic alias so BOTH of the following work and
call the exact same underlying code (no duplicated logic, cannot drift out
of sync with each other):

    from jhora.horoscope.dhasa.graha import dwisaptati
    from jhora.horoscope.dhasa.graha import dwisatpathi

Usage is identical either way, e.g.:
    dwisaptati.get_dhasa_bhukthi(...)
    dwisatpathi.get_dhasa_bhukthi(...)
are the same function object.
"""
from jhora.horoscope.dhasa.graha.dwisatpathi import *  # noqa: F401,F403

# `import *` only picks up names that do not start with an underscore, which
# covers every PUBLIC function/constant in dwisatpathi.py (get_dhasa_bhukthi,
# get_running_dhasa_for_given_date, dwisatpathi_immediate_children,
# nakshathra_dhasa_progression, applicability_check, dhasa_adhipathi_list,
# seed_lord, count_direction, year_duration,
# human_life_span_for_dwisatpathi_dhasa, etc.) -- nothing extra to add there.

# Also expose the dwisatpathi-named public function under a
# "dwisaptati"-named alias, for callers who expect the function name itself
# (not just the module name) to match the Sanskrit spelling.
from jhora.horoscope.dhasa.graha.dwisatpathi import (
    get_immediate_children as dwisaptati_immediate_children,
)
