#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Shared UI components and page state for all JHoraWeb pages.
  ensure_default_state()          per-browser page state (birth details in memory, other keys in
                                  app.storage.user)
  search_places_in_db()           place search in the SQLite places database
  navigation_header()             navigation bar shown at the top of every page
  render_control_bar()            two-row birth-details / control bar used by the calculation pages
  render_birth_details_bar()      single-row birth-details bar (older layout)
  render_full_panchangam_popup()  dialog with the full panchangam
  print_button()                  "Print / Save as PDF" button that triggers the browser's own print
                                  dialog.
  trigger_print_js()              runs window.print()-containing JavaScript correctly (see below).
  DelayedBusyIndicator            non-intrusive "please wait" UI that only appears if a worker-thread
                                  computation is still running after a short delay (see its class
                                  docstring); used across the calculation pages.
calc_lock, apply_current_language, safe_notify and ignore_disconnected_client are re-exported
from engine_sync.
Print CSS summary (see _PRINT_CSS below for the actual rules)
---------------------------------------------------------------
Single-chart print/PDF (kundali_chart.py's print_button()): the page's own
'.print-three-col-layout' row (chart info col 1, chart info col 2, chart) is laid out as a CSS Grid
with the chart column sized 'auto' (not a fixed fraction), so with the two text columns kept compact
('print-compact-text') there is real spare width on an A4-landscape page for the chart to be drawn
considerably larger ('chart-surface') than its on-screen default.
Multi-page "Save All Vargas as PDF" report, multi-column plain-text layouts, generic "print only"
utility, multi-dhasa report classes - see their own inline comments below for full history; not
repeated here.
IMPORTANT (print) - "full-bleed table width" rule and its UNINTENDED side effect on side-by-side
tables:
  `table { width: 100% !important; }` below was added early in this project to fix ONE specific
  problem: a single raw HTML <table> built as a plain string (e.g. Kundali's/Bhava's own information
  panel) was sizing itself to its own CONTENT width rather than filling the wider grid column the
  full-bleed fix (just above it) had made available. Applied globally, this ALSO affects every OTHER
  <table> anywhere else in the app's print output - including several newer pages (Amsa Ruler, Saham,
  Drishti, Argala, and several Strength pages) that intentionally place TWO OR MORE tables NEXT TO
  EACH OTHER in a row. Forcing every one of them to 100% width means NONE of them can fit beside
  another - each claims the full row, so they stack vertically instead, overflowing what should be
  ONE compact page into several mostly-empty extra ones.
  '.print-side-by-side' is the fix: applied to the ROW/container holding tables meant to sit next to
  each other.
    - It re-enables wrapping and explicitly opts any <table> INSIDE it back OUT of the global
      100%-width rule (back to its own natural/auto width).
    - It resets each side-by-side box's own on-screen fixed minimum width (e.g. Tailwind's
      min-w-[520px]) back to 0, so a box shrinks to fit its own content instead of forcing a width
      that, combined with its neighbor's own fixed width, is wider than one landscape page can hold
      side by side.
    - It shrinks the print font size of everything inside to 8pt, to help 2+ individually-wide
      tables (long planet names, several-column layouts) actually fit side by side.
      IMPORTANT CSS-SPECIFICITY NOTE (found the hard way - confirmed from an ACTUAL printed PDF that
      Drishti specifically still took 2 pages even after this class was applied elsewhere): CSS
      inheritance of font-size from an ANCESTOR only applies to a descendant that does NOT have its
      OWN explicit font-size. Several pages' <table> elements carry Tailwind's own 'text-sm' utility
      class DIRECTLY on the <table> tag itself (e.g. `.classes('border-collapse text-sm w-full')`) -
      that is an explicit, direct declaration on the table, so the table's OWN font-size (from
      text-sm, ~14px) is used regardless of whatever font-size the row ABOVE it (the one carrying
      '.print-side-by-side') is set to, with or without !important on that ancestor rule - `!important`
      only affects how a property is weighed AT THE SAME ELEMENT during the cascade; it does nothing
      to make an ancestor's declared value override a MORE SPECIFIC declaration made directly on a
      descendant element. This is why `.print-side-by-side { font-size: 8pt !important; }` alone was
      not enough for a page whose table happens to set its own font-size directly - it was "working"
      only by accident on pages whose nested elements happened to have no explicit font-size of their
      own, so they picked up the inherited 8pt. The actual, robust fix needs a selector that matches
      the table/its descendants DIRECTLY (not just the ancestor row), with equal-or-higher
      specificity than Tailwind's own utility classes - `body .print-side-by-side, body
      .print-side-by-side *` below does this: adding the `body` element to the selector gives it
      specificity (0,1,1), which reliably beats a plain one-class Tailwind utility like `.text-sm`
      (specificity (0,1,0)) regardless of which stylesheet loads first or which rule is written
      later in the page - a tie on specificity would otherwise be decided by order, which is NOT
      something this project controls (Tailwind's own utility stylesheet's load order relative to
      this page's own <style> block is not guaranteed).
  '.print-attach-next' (NEW): keeps a short, standalone heading/title attached to the START of
  whatever immediately follows it (typically one table) - without this, a page break can land
  between a heading and its own content even when nothing is overcrowded. Also carries
  `break-before: avoid` (added after an actual printed PDF showed a page genuinely left BLANK first -
  KP-Lord: the title+table pair, together, did not fit the remaining space on a page and was pushed
  as a whole unit to the next page instead of splitting, the same class of "lone first-of-page
  element pushed entirely to the next page" behavior already fixed once for the other print layout
  classes below).
Stray Quasar notifications (safe_notify() toasts) during print are hidden unconditionally
(.q-notification, .q-notifications) - these are NOT scoped to any one page's content.
IMPORTANT for any JavaScript that runs `window.print()`: use `await trigger_print_js(script)` below
instead of calling ui.run_javascript(...) directly - see that function's own docstring for why (must
be awaited DIRECTLY in the caller's handler, never deferred via asyncio.ensure_future, never passed
`respond=False`).
IMPORTANT NOTE ON PAGE RECONNECTS: NiceGUI page functions (anything decorated with @ui.page) can
re-run from scratch on a browser reconnect - this was confirmed to happen specifically around
window.print() in at least one browser/printer-driver combination. Any state a page needs to
survive this MUST be stored in app.storage.user (e.g. via the page's own `state` object from
ensure_default_state()), never in a plain local Python variable/dict created fresh inside the page
function - see dhasa_tab.py's _get_dhasa_options()/_set_dhasa_options() and
_get_selection()/_set_selection() for two worked examples of this pattern.
"""
import asyncio
import contextvars
import os
import sqlite3
from datetime import datetime
from nicegui import ui, app, run
from jhora import const, utils
from options_dialog import open_options_dialog
import birth_store
import web_settings
from row_fit import fit_css, fit_row  # one-line control rows without a scrollbar (see row_fit.py)
import calc_highlight
import tz_sync
from privacy_notice import show_privacy_notice
from engine_sync import (  # noqa: F401  (re-exported for convenience)
  calc_lock, apply_current_language, safe_notify, ignore_disconnected_client,
)
import os
_WEB_VERSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_web_version.txt')
with open(_WEB_VERSION_PATH, encoding='utf-8') as f:
    WEB_APP_VERSION = f.read().strip()
_PRINT_CSS = """
<style>
  @media print {
    @page { size: A4 landscape; margin: 6mm; }
    html, body { background: white !important; height: auto !important; overflow: visible !important; margin: 0 !important; padding: 0 !important; }
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    .no-print { display: none !important; }
    /* Full-bleed fix: NiceGUI/Quasar's own page wrapper elements commonly carry a fixed or
       viewport-relative max-width for on-screen responsive layout. This removes that constraint so
       page content genuinely fills the printable area.
       'background: white !important' (ADDED here): _PAGE_THEME_CSS below sets a permanent,
       non-print-scoped 'body, .q-page { background-color: #f6f7f5; }' (the app's on-screen light-grey
       site background) - the 'html, body { background: white !important; ...}' rule just above only
       resets the <html>/<body> ELEMENTS themselves; it does NOT touch '.q-page' (the actual Quasar
       content wrapper DIV that carries the visible grey), so that grey background survived into both
       the print PREVIEW and the saved PDF even with the browser's own "Background graphics" print
       option left UNCHECKED - confirmed from an actual printed PDF/preview (v0.9.4) showing every
       page on a grey, not white, background. Adding 'background: white !important' to this SAME
       selector list (which already names every relevant wrapper element: .q-page, .nicegui-content,
       .q-layout, .q-layout-container, .q-page-container) fixes all of them in one place, consistent
       with how 'width'/'max-width'/'margin' are already reset here for the exact same set of
       elements. */
    html, body, .nicegui-content, .q-page, .q-layout, .q-layout-container, .q-page-container {
      width: 100% !important; max-width: none !important; margin: 0 !important;
      background: white !important;
    }
    /* See the module docstring's "full-bleed table width" note above for why this exists AND for
       its unintended side effect on side-by-side tables, fixed below by '.print-side-by-side'. */
    table { width: 100% !important; }
    .q-notification, .q-notifications { display: none !important; }
    table, tr, .q-card { break-inside: avoid !important; page-break-inside: avoid !important; }
    .print-expand {
      max-height: none !important; overflow: visible !important;
      overflow-x: visible !important; overflow-y: visible !important;
    }
    .print-compact-text { font-size: 6pt !important; line-height: 1.1 !important; }
    /* --- See the module docstring's "full-bleed table width" note for the full history of both
       classes below, INCLUDING the CSS-specificity bug found and fixed in the font-size rule. --- */
    .print-side-by-side {
      display: flex !important; flex-wrap: wrap !important;
      overflow: visible !important; overflow-x: visible !important; overflow-y: visible !important;
      page-break-before: avoid !important; break-before: avoid !important;
    }
    .print-side-by-side > table, .print-side-by-side table {
      width: auto !important;
    }
    .print-side-by-side > * {
      min-width: 0 !important;
    }
    /* `body .print-side-by-side` / `body .print-side-by-side *`: the `body` element is included
       specifically to raise this selector's specificity to (0,1,1), which reliably beats a plain
       one-class Tailwind utility like `.text-sm` (specificity (0,1,0)) regardless of stylesheet
       load order - seethe module docstring's CSS-specificity note for the full explanation of why
       a plain `.print-side-by-side { font-size: 8pt !important; }` rule (an EARLIER, insufficient
       version of this fix) did not actually shrink a <table> that carries its own explicit
       font-size utility class directly on the <table> tag itself (confirmed from an actual printed
       PDF: Drishti's own tables, which do exactly this, still did not shrink and still took 2
       pages, despite that earlier rule already being in place). */
    body .print-side-by-side, body .print-side-by-side * {
      font-size: 8pt !important; line-height: 1.2 !important;
    }
    .print-attach-next {
      break-after: avoid !important; page-break-after: avoid !important;
      break-before: avoid !important; page-break-before: avoid !important;
    }
    .print-three-col-layout {
      display: grid !important;
      grid-template-columns: 1fr 1fr auto !important;
      gap: 6pt !important;
      align-items: start !important;
      width: 100% !important;
      height: auto !important;
      max-height: none !important;
      overflow: visible !important;
      page-break-before: avoid !important;
      break-before: avoid !important;
      margin-top: 0 !important;
    }
    .print-info-col { width: 100% !important; max-width: none !important; }
    .print-chart-col { display: flex !important; flex-direction: column !important; align-items: center !important; }
    .print-two-col-layout {
      display: grid !important;
      grid-template-columns: 1fr auto !important;
      gap: 6pt !important;
      align-items: start !important;
      width: 100% !important;
      height: auto !important;
      max-height: none !important;
      overflow: visible !important;
      page-break-before: avoid !important;
      break-before: avoid !important;
      margin-top: 0 !important;
    }
    .print-two-col-layout .chart-surface { width: 480px !important; height: 480px !important; }
    .print-two-col-layout .chart-surface .chart-cell { height: 96px !important; }
    .print-two-col-layout .chart-surface .chart-cell-text { font-size: 10pt !important; line-height: 1.1 !important; }
    .print-two-col-layout .chart-surface .chart-rasi-badge { font-size: 8pt !important; }
    .print-two-col-layout .chart-surface .chart-overlay-text { font-size: 8pt !important; }
    .print-two-col-layout .print-compact-text { font-size: 9pt !important; line-height: 1.3 !important; }
    .chart-surface { width: 320px !important; height: 320px !important; padding: 4px !important; gap: 2px !important; }
    .chart-surface .chart-cell { height: 64px !important; padding: 1px !important; }
    .chart-surface .chart-cell-text { font-size: 7pt !important; line-height: 1.05 !important; }
    .chart-surface .chart-rasi-badge { font-size: 6pt !important; line-height: 1 !important; }
    .chart-surface .chart-overlay-text { font-size: 6pt !important; line-height: 1.05 !important; }
    .all-charts-report { display: none !important; }
    body.printing-all .single-chart-print-block { display: none !important; }
    body.printing-all .all-charts-report { display: block !important; }
    .print-report-page { break-inside: avoid !important; page-break-inside: avoid !important; }
    .print-report-page-break { break-before: page !important; page-break-before: always !important; }
    .dhasa-report-item {
      margin-bottom: 10pt !important;
      break-inside: auto !important; page-break-inside: auto !important;
      break-before: avoid !important; page-break-before: avoid !important;
    }
    .dhasa-report-item table { font-size: 8pt !important; }
    .dhasa-report-item td, .dhasa-report-item th {
      font-size: 8pt !important; line-height: 1.15 !important; padding: 2pt 6pt !important;
    }
    .dhasa-report-header {
      break-inside: avoid !important; page-break-inside: avoid !important;
      break-after: avoid !important; page-break-after: avoid !important;
    }
    .print-cols3 {
      display: grid !important;
      grid-template-columns: 1fr 1fr 1fr !important;
      gap: 8pt !important;
      align-items: start !important;
      width: 100% !important;
      overflow: visible !important;
      page-break-before: avoid !important;
      break-before: avoid !important;
    }
    .print-cols3 > div, .print-cols3 .q-card {
      break-inside: auto !important; page-break-inside: auto !important;
    }
    .print-only { display: block !important; }
  }
  .all-charts-report { display: none; }
  .print-only { display: none; }
</style>
"""
DB_PATH = os.environ.get("JHORA_PLACES_DB") or (const._DATA_DIR + const._sep + "geonames_places_5k.db")
TITHI_ICONS = {
  3: 'third_crescent.png', 8: 'ashtami.png', 9: 'navami.png',
  15: 'pournami.png', 23: 'ashtami.png', 24: 'navami.png', 30: 'amavasai.png'
}
_DEFAULT_PLACE_NAME = "Chennai"
_DEFAULT_LATITUDE = "13.0878"
_DEFAULT_LONGITUDE = "80.2785"
_DEFAULT_TIMEZONE = "5.5"
_MAX_LOCATION_RESOLVE_ATTEMPTS = 3
_IP_LOCATION_CACHE = {}        # public IP address -> [place, latitude, longitude, time zone]; successful lookups only
_IP_LOCATION_CACHE_MAX = 500
_IP_LOCATION_LOGGED = set()     # messages already printed once (keeps the console readable)
_PLACE_STATE_KEYS = ("place_name", "latitude", "longitude", "timezone")
_LOC_DONE_KEY = "_loc_ip_done"            # saved with the browser: the IP lookup succeeded
_LOC_ATTEMPTS_KEY = "_loc_ip_attempts"    # saved with the browser: number of failed tries
_OLD_LOC_KEYS = ("_location_resolved", "_location_resolve_attempts")
_LOC_CLOCK_KEY = "_loc_ip_clock_pending"   # saved with the browser: date/time of birth should follow the located place
def res_str(key, fallback):
  """Returns the language resource string for `key`, or `fallback` if it is not available."""
  try:
      return utils.resource_strings.get(key, fallback)
  except Exception:
      return fallback
def ensure_default_state():
  """Creates (if missing) and returns this browser's page state."""
  birth_store.purge_from_disk_storage()
  dropped = web_settings.migrate_overrides()
  if dropped:
      safe_notify('This version changed some options, so your saved choice was reset for: '
                  + ', '.join(dropped[:5]) + (' ...' if len(dropped) > 5 else ''), type='info')
  s = birth_store.SessionState()
  now = datetime.now()
  _str = lambda v: isinstance(v, str)
  _int = lambda v: isinstance(v, int) and not isinstance(v, bool)
  schema = {
      "date_dob": (lambda: now.strftime('%Y,%m,%d'), _str),
      "time_tob": (lambda: now.strftime('%H:%M:%S'), _str),
      "place_name": (lambda: _DEFAULT_PLACE_NAME, _str),
      "latitude": (lambda: _DEFAULT_LATITUDE, _str),
      "longitude": (lambda: _DEFAULT_LONGITUDE, _str),
      "timezone": (lambda: _DEFAULT_TIMEZONE, _str),
      "gender": (lambda: int(const.GENDER.FEMALE), lambda v: _int(v) and v in (0, 1)),
      "cal_date": (lambda: now.strftime('%Y,%m,%d'), _str),
      "cal_system": (lambda: "SOLAR", _str),
      "kundali_chart_style_index": (lambda: 0, lambda v: _int(v) and v >= 0),
      "kundali_chart_style": (lambda: "south_indian_regular", _str),
  }
  place_defaulted = False
  clock_defaulted = False
  for key, (default, ok) in schema.items():
      try:
          valid = key in s and ok(s[key])
      except Exception:
          valid = False
      if not valid:
          s[key] = default()
          if key in _PLACE_STATE_KEYS:
              place_defaulted = True
          if key in ("date_dob", "time_tob"):
              clock_defaulted = True
  if place_defaulted:
      # The place fields live in server MEMORY only (birth_store: lost on restart or after the idle
      # timeout), but the lookup flags below are kept in app.storage.user, which survives. Without this
      # reset a browser that already had a lookup recorded would stay on the default place for good.
      for key in (_LOC_DONE_KEY, _LOC_ATTEMPTS_KEY):
          s.pop(key, None)
  if clock_defaulted:
      # date/time of birth now hold the SERVER's clock; replace it by the located place's local time once
      # the lookup succeeds. Not set when the visitor's own date/time are still in memory (never overwritten).
      s[_LOC_CLOCK_KEY] = True
  for key in _OLD_LOC_KEYS:       # flags written by older versions (they marked the lookup done even when it was OFF)
      s.pop(key, None)
  resolve_initial_location(s)
  return s
def _location_log(message, once=False):
  """Prints a '[location]' line to the console so it is visible WHY a place was or was not found."""
  if once:
      if message in _IP_LOCATION_LOGGED:
          return
      _IP_LOCATION_LOGGED.add(message)
  print(f"[location] {message}")
def _visitor_ip_address():
  """Returns the public IP address of the visitor's BROWSER, read from the current HTTP request (the
  proxy headers first, then the connection itself).
  '' means the request came from a private/loopback address, i.e. the browser and the server are on the
  same machine or network; None means there is no request to read an address from."""
  import ipaddress
  try:
      request = ui.context.client.request
  except Exception:
      return None
  if request is None:
      return None
  candidates = []
  try:
      headers = request.headers
      for name in ('cf-connecting-ip', 'x-real-ip'):
          if headers.get(name):
              candidates.append(headers.get(name))
      forwarded = headers.get('x-forwarded-for')
      if forwarded:
          candidates.append(forwarded.split(',')[0])      # the first entry is the original client
      if request.client:
          candidates.append(request.client.host)
  except Exception:
      pass
  for text in candidates:
      try:
          address = ipaddress.ip_address(str(text).strip())
      except ValueError:
          continue
      mapped = getattr(address, 'ipv4_mapped', None)      # ::ffff:a.b.c.d -> a.b.c.d
      if mapped is not None:
          address = mapped
      if address.is_global:
          return str(address)
  return ''
_IP_LOOKUP_TIMEOUT = 4          # seconds to wait for each lookup service
_IP_LOOKUP_USER_AGENT = "SarvaJyotish/1.0"
def _ip_lookup_services(ip_address):
  """Free IP-geolocation services in the order they are tried: [(name, url, extra_headers, parser)].
  A parser takes the decoded JSON and returns (latitude, longitude, city, country_code), or None when the
  service has no answer for this address."""
  import os
  def _ipinfo(d):
      latitude, longitude = str(d["loc"]).split(",")
      return float(latitude), float(longitude), d.get("city", ""), d.get("country", "")
  def _ipwho(d):
      if d.get("success") is False:
          return None
      return float(d["latitude"]), float(d["longitude"]), d.get("city", ""), d.get("country_code", "")
  def _geojs(d):
      return float(d["latitude"]), float(d["longitude"]), d.get("city", ""), d.get("country_code", "")
  def _ipapi(d):
      if d.get("error"):
          return None
      return float(d["latitude"]), float(d["longitude"]), d.get("city", ""), d.get("country_code", "")
  def _freeipapi(d):
      return float(d["latitude"]), float(d["longitude"]), d.get("cityName", ""), d.get("countryCode", "")
  services = []
  token = os.environ.get("IPINFO_TOKEN", "").strip()
  if token:       # sent as a header, never in the URL, so it cannot end up in an error message or log
      services.append(("ipinfo.io", f"https://ipinfo.io/{ip_address}/json", {"Authorization": f"Bearer {token}"}, _ipinfo))
  services += [
      ("ipwho.is", f"https://ipwho.is/{ip_address}", {}, _ipwho),
      ("geojs.io", f"https://get.geojs.io/v1/ip/geo/{ip_address}.json", {}, _geojs),
      ("ipapi.co", f"https://ipapi.co/{ip_address}/json/", {}, _ipapi),
      ("freeipapi.com", f"https://freeipapi.com/api/json/{ip_address}", {}, _freeipapi),
  ]
  return services
def _place_from_ip_address(ip_address):
  """Returns [place, latitude, longitude, time zone offset] for a public IP address, or [] when it cannot
  be located. Successful lookups are cached per IP address (failures are not, so a temporary network
  problem or a throttled service does not stick)."""
  cached = _IP_LOCATION_CACHE.get(ip_address)
  if cached:
      return list(cached)
  import requests
  base_headers = {"User-Agent": _IP_LOOKUP_USER_AGENT, "Accept": "application/json"}
  found = None
  for name, url, extra_headers, parser in _ip_lookup_services(ip_address):
      try:
          response = requests.get(url, headers={**base_headers, **extra_headers}, timeout=_IP_LOOKUP_TIMEOUT)
          response.raise_for_status()
          found = parser(response.json())
          if found is not None:
              latitude, longitude = found[0], found[1]
              # a service that does not know the address may answer 0,0 or garbage: treat as "no answer"
              if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0) or (latitude == 0.0 and longitude == 0.0):
                  found = None
      except requests.HTTPError as e:
          # only the status code is logged: the exception text contains the URL, i.e. the visitor's IP address
          _location_log(f"lookup service {name}: HTTP {getattr(e.response, 'status_code', '?')} - trying the next one.", once=True)
          found = None
          continue
      except Exception as e:
          _location_log(f"lookup service {name}: {type(e).__name__} - trying the next one.", once=True)
          found = None
          continue
      if found is not None:
          _location_log(f"lookup service {name} answered.", once=True)
          break
  if found is None:
      return []
  latitude, longitude, city, country = found
  place = f"{city or ''},{country or ''}".strip(',') or f"{latitude:.4f},{longitude:.4f}"
  result = [place, latitude, longitude, float(utils.get_place_timezone_offset(latitude, longitude))]
  if len(_IP_LOCATION_CACHE) >= _IP_LOCATION_CACHE_MAX:
      _IP_LOCATION_CACHE.clear()
  _IP_LOCATION_CACHE[ip_address] = result
  return list(result)

def resolve_initial_location(state):
  """Sets the place fields of `state` from the visitor's IP address when
  const.use_internet_for_location_check is on. When the location cannot be found, the defaults set by
  ensure_default_state() (Chennai) stay.
  A visitor on a public IP address is located from THAT address (the browser's). The PyJHora function
  utils.get_place_from_user_ip_address() looks up the address of the machine running this code, so it is
  only used when the browser is on the same machine/network as the server (private or loopback address);
  on a public server it would put every visitor in the server's city."""
  if state.get(_LOC_DONE_KEY):
      return
  attempts = state.get(_LOC_ATTEMPTS_KEY, 0)
  if attempts >= _MAX_LOCATION_RESOLVE_ATTEMPTS:
      state.pop(_LOC_CLOCK_KEY, None)         # gave up: keep the server clock, stop waiting
      return
  use_internet = getattr(const, 'use_internet_for_location_check', False)
  if not use_internet:
      # Not remembered in `state`: that is saved with the browser session, and would stop the lookup from
      # ever running for this browser after the setting is switched on.
      _location_log("const.use_internet_for_location_check is OFF - keeping the default place. "
                    "Set it to True to find the visitor's place from the IP address.", once=True)
      state.pop(_LOC_CLOCK_KEY, None)
      return
  visitor_ip = _visitor_ip_address()
  if visitor_ip is None:      # no request to read the address from: keep the defaults, try again later
      _location_log("no HTTP request available to read the visitor's IP address - keeping the default place.", once=True)
      return
  state[_LOC_ATTEMPTS_KEY] = attempts + 1
  try:
      if visitor_ip:
          #_location_log(f"visitor IP address {visitor_ip} - looking it up (attempt {attempts + 1}/{_MAX_LOCATION_RESOLVE_ATTEMPTS}).")
          loc = _place_from_ip_address(visitor_ip)
      else:
          _location_log(f"browser is on a private/loopback address - using the server machine's own IP address "
                        f"(attempt {attempts + 1}/{_MAX_LOCATION_RESOLVE_ATTEMPTS}).")
          with calc_lock():
              loc = utils.get_place_from_user_ip_address()
          if not loc:
              # utils caches even a FAILED lookup (functools.lru_cache), so without this it would stay [] until restart.
              try:
                  utils._get_place_from_user_ip_address_cached.cache_clear()
              except Exception:
                  pass
      if loc and len(loc) >= 4:
          #_location_log(f"found: {loc[0]} lat={loc[1]} lon={loc[2]} tz={loc[3]}")
          state.update({
              "place_name": str(loc[0]), "latitude": str(loc[1]),
              "longitude": str(loc[2]), "timezone": str(loc[3]),
          })
          state[_LOC_DONE_KEY] = True
          if state.get(_LOC_CLOCK_KEY):
              # the Time field must be the local time AT the located place, not the server's clock
              try:
                  from datetime import timezone as _tz, timedelta as _td
                  local_now = datetime.now(_tz.utc) + _td(hours=float(loc[3]))
                  state.update({"date_dob": local_now.strftime('%Y,%m,%d'),
                                "time_tob": local_now.strftime('%H:%M:%S')})
                  #_location_log(f"date/time set to the local time at {loc[0]} (UTC{float(loc[3]):+g}): "
                  #              f"{local_now.strftime('%Y-%m-%d %H:%M:%S')}")
              except Exception as e:
                  _location_log(f"could not set the local time: {type(e).__name__}: {e}")
          state.pop(_LOC_CLOCK_KEY, None)
      else:
          _location_log(f"no usable result (attempt {attempts + 1}/{_MAX_LOCATION_RESOLVE_ATTEMPTS}) - keeping the default place.")
  except Exception as e:
      _location_log(f"lookup failed (attempt {attempts + 1}/{_MAX_LOCATION_RESOLVE_ATTEMPTS}): {type(e).__name__}: {e}")
def search_places_in_db(query_text: str):
  """Searches the places database for a name (accent- and case-insensitive substring match on the
  place label or its aliases). Returns up to 20 rows; [] on a database error or too-short text."""
  import unicodedata, re
  if not query_text or len(query_text.strip()) < 2:
      return []
  def normalize_text(text):
      if not text: return ""
      text = unicodedata.normalize("NFKD", text)
      text = "".join(ch for ch in text if not unicodedata.combining(ch))
      text = text.lower()
      text = re.sub(r"[^a-z0-9]+", " ", text)
      return re.sub(r"\s+", " ", text).strip()
  try:
      norm_query = normalize_text(query_text)
      conn = sqlite3.connect(DB_PATH)
      cursor = conn.cursor()
      cursor.execute(
          """
          SELECT DISTINCT p.display_label, p.latitude, p.longitude, p.timezone_hours, p.elevation
          FROM places p JOIN aliases a ON p.id = a.place_id
          WHERE a.alias_norm LIKE ? OR p.display_label_norm LIKE ?
          ORDER BY p.display_label LIMIT 20
          """, (f"%{norm_query}%", f"%{norm_query}%")
      )
      rows = cursor.fetchall()
      conn.close()
      return rows
  except Exception as e:
      print(f"Database search error: {e}")
      return []
_TAB_CLASSES = (
  'text-white text-xs font-medium no-underline shrink-0 '
  'px-2.5 py-1.5 hover:bg-green-700 transition-colors'
)
def _nav_tab_link(label, path):
  ui.link(label, path).classes(_TAB_CLASSES)
def _nav_dropdown(label, items):
  with ui.button(label).props('flat dense no-caps color=white').classes(_TAB_CLASSES + ' min-h-0 rounded-none'):
      ui.icon('expand_more').classes('text-xs ml-1')
      with ui.menu().props('auto-close').classes('bg-white'):
          with ui.column().classes('gap-0 py-1'):
              for text, path in items:
                  ui.link(text, path).classes(
                      'block px-4 py-1.5 text-black text-xs no-underline hover:bg-green-50 whitespace-nowrap'
                  )
_PAGE_THEME_CSS = """
<style>
  .nicegui-content, .q-page { padding: 0 !important; }
  body, .q-page { background-color: #f6f7f5; }
  .q-separator { margin-top: 4px !important; margin-bottom: 4px !important; }
  .q-field__label { line-height: 1.1; }
</style>
"""
_PAGE_THEME_CSS += '<style>' + fit_css() + '</style>'
_PAGE_THEME_CSS += _PRINT_CSS
# ---------------------------------------------------------------------------------------------------
# Right-to-left (RTL) languages. When the visitor's language is one of these, every page gets
# dir="rtl" on <html> (the browser then mirrors the layout: nav bar, headings, cards, text alignment).
# Charts (.chart-surface) and anything marked 'keep-ltr' stay left-to-right, because a mirrored chart
# would put the signs in the wrong cells.
# ---------------------------------------------------------------------------------------------------
RTL_LANGUAGES = {"ur", "ar", "fa", "he", "ps", "kaa"}      # language codes (as in available_languages)
_RTL_LANGUAGE_NAMES = {"urdu", "arabic", "persian", "farsi", "hebrew", "pashto", "kashmiri/arab"}
def _visitor_language():
  """Returns the current visitor's language code, lower-case: the visitor's own language in public mode,
  otherwise the server's language (const._DEFAULT_LANGUAGE)."""
  lang = None
  try:
      import web_language
      lang = web_language._active_language()      # None when the visitor uses the server's language
  except Exception:
      pass
  return str(lang or getattr(const, '_DEFAULT_LANGUAGE', 'en') or 'en').strip().lower()
def is_rtl_language(lang=None):
  """True if `lang` (default: the visitor's language) is written right to left."""
  lang = (str(lang).strip().lower() if lang else _visitor_language())
  return lang in RTL_LANGUAGES or lang in _RTL_LANGUAGE_NAMES
_RTL_HEAD_HTML = r"""
<!-- rtl-signed-numbers v2 | rtl-overlays v4 -->
<script>
(function () {
  var LRM = '\u200E';
  var SIGNED = /(^|[\s(])([+\-]\d+(?:\.\d+)?)/g;
  function mark(node) {
    var t = node.nodeValue;
    if (!t || (t.indexOf('+') === -1 && t.indexOf('-') === -1)) { return; }
    var u = t.replace(SIGNED, function (m, pre, num) { return pre + LRM + num + LRM; });
    if (u !== t) { node.nodeValue = u; }
  }
  function walk(root) {
    if (root.nodeType === 3) { mark(root); return; }
    if (root.nodeType !== 1) { return; }
    var tag = root.nodeName;
    if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA') { return; }
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) { mark(n); }
  }
  new MutationObserver(function (list) {
    for (var i = 0; i < list.length; i++) {
      var m = list[i];
      if (m.type === 'characterData') { mark(m.target); }
      else { for (var j = 0; j < m.addedNodes.length; j++) { walk(m.addedNodes[j]); } }
    }
  }).observe(document.documentElement, {childList: true, subtree: true, characterData: true});
  document.addEventListener('DOMContentLoaded', function () { walk(document.body); });
})();
</script>
<script>
(function () {
  var ARABIC = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  var html = document.documentElement;
  var OVERLAYS = '.q-dialog, .q-menu, .q-tooltip, .q-notification';
  // the page direction lives on the app container, not on <html>: Quasar's [dir=rtl] and [dir=ltr] rule sets
  // are both applied to anything that has an ancestor with each attribute, so <html dir=rtl> would also apply
  // the RTL rules to every English dialog
  function pageDir() {
    if (html.hasAttribute('dir')) { html.removeAttribute('dir'); }
    var app = document.getElementById('app');
    if (app && app.getAttribute('dir') !== 'rtl') { app.setAttribute('dir', 'rtl'); }
    ['q-notify', 'q-loading-bar'].forEach(function (id) {
      var e = document.getElementById(id); if (e && e.getAttribute('dir') !== 'rtl') { e.setAttribute('dir', 'rtl'); }
    });
  }
  function overlays() {
    var list = document.querySelectorAll(OVERLAYS);
    for (var i = 0; i < list.length; i++) {
      var el = list[i];
      if (el.getAttribute('data-rtl-final')) { continue; }
      var t = el.textContent || '';
      if (ARABIC.test(t)) { el.setAttribute('dir', 'rtl'); el.setAttribute('data-rtl-final', '1'); }
      else if (t.replace(/\s+/g, '').length >= 3) { if (el.getAttribute('dir') !== 'ltr') { el.setAttribute('dir', 'ltr'); } }
      else if (!el.getAttribute('dir')) { el.setAttribute('dir', 'rtl'); }      // empty / still loading: follow the page
    }
  }
  var queued = false;
  new MutationObserver(function () {
    if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; pageDir(); overlays(); }); }
  }).observe(html, {attributes: true, attributeFilter: ['dir'], childList: true, subtree: true, characterData: true});
  pageDir();
  document.addEventListener('DOMContentLoaded', function () { pageDir(); overlays(); });
})();
</script>
<style>
  /* the page itself is right-to-left (the dir attribute is on the app container, see above) */
  html { direction: rtl; }
  /* charts and anything marked keep-ltr are never mirrored */
  .chart-surface, .keep-ltr { direction: ltr !important; }
  .q-field__native, .q-field__input { unicode-bidi: plaintext; }
</style>
"""
def _get_app_name_version():
   return res_str('app_version_name_str',const._APP_NAME) + ' V' + WEB_APP_VERSION

def navigation_header():
  """Adds the page CSS, shows the privacy notice and the navigation bar. Call it first on every page.
  The navigation bar itself is marked 'no-print'.
  """
  ui.add_head_html(_PAGE_THEME_CSS)
  if is_rtl_language():
      ui.add_head_html(_RTL_HEAD_HTML)
  show_privacy_notice()
  _APP_NAME_VERSION = _get_app_name_version()
  _ydp_nls = res_str('yoga_str',"Yoga") + ' / ' + res_str('dosha_str','Dosha') + ' / ' + res_str('general_prediction_str', 'Prediction')
  with ui.header().classes('bg-green-800 text-white flex items-center px-2 py-0 gap-2 min-h-0 no-print'):
      ui.label(_APP_NAME_VERSION).classes('text-sm font-bold shrink-0')
      with ui.row().classes('items-stretch gap-0 divide-x divide-green-600/60 flex-nowrap overflow-x-auto'):
          _nav_tab_link(res_str('panchangam_str', 'Panchangam'), '/')
          _nav_tab_link(res_str('calendar_str', 'Vedic Calendar'), '/calendar')
          _nav_dropdown(res_str('charts_str', 'Charts'), [
              (res_str('horoscope_str', 'Kundali'), '/kundali'),
              (res_str('bhaava_str', 'Bhava'), '/bhava'),
              (res_str('chakra_str', 'Chakra'), '/chakra'),
              (res_str('transit_str', 'Transit'), '/transit'),
          ])
          _db_str = res_str('dhasa_str', 'Dhasa') + '/' + res_str('bhukthi_str', 'Bhukthi')
          _nav_tab_link(_db_str, '/dhasa')
          _nav_dropdown(res_str('compute_str', 'Calculations'), [
              (res_str('amsa_ruler_str', 'Amsa Ruler'), '/amsa_ruler'),
              (res_str('sphuta_str', 'Sphuta'), '/sphuta'),
              (res_str('saham_str', 'Saham'), '/saham'),
              (res_str('drishti_str', 'Drishti'), '/drishti'),
              (res_str('bhava_graha_arudha_str', 'Arudha'), '/arudha'),
              (res_str('ashtaka_varga_str', 'Ashtakavarga'), '/ashtakavarga'),
              (res_str('argala_str', 'Argala'), '/argala'),
              (res_str('shodhaya_pinda_str', 'Shodhaya Pinda'), '/shodhaya_pinda'),
              ('KP-'+res_str('lord_str','Lord'), '/kpinfo'),
              (res_str('vrathas_str', 'Vrathas'), '/vratha'),
          ])
          _nav_dropdown(res_str('strength_str', 'Strength'), [
              (res_str('vimsopaka_bala_str', 'Vimsopaka Bala'), '/vimsopaka_bala'),
              (res_str('vaiseshikamsa_bala_str', 'Vaiseshikamsa Bala'), '/vaiseshikamsa_bala'),
              (res_str('harsha_pancha_dwadhasa_vargeeya_bala_str', 'Other Bala'), '/other_bala'),
              (res_str('shad_bala_str', 'Shad Bala'), '/shad_bala'),
              (res_str('bhava_bala_str', 'Bhava Bala'), '/bhava_bala'),
          ])
          _nav_dropdown(_ydp_nls, [
              (res_str('yoga_str', 'Yoga'), '/yoga'),
              (res_str('dosha_str', 'Dosha'), '/dosha'),
              (res_str('general_prediction_str', 'Prediction'), '/prediction'),
          ])
          _nav_tab_link(res_str('compatibility_str', 'Compatibility'), '/compatibility')
          _nav_tab_link(res_str('pancha_pakshi_sastra_str', 'Pancha Pakshi'), '/pancha_pakshi')
          _nav_tab_link(res_str('about_str', 'About'), '/about')

def _footer_inner_html():
    """The footer's actual content (copyright + download link + visitor badge), as plain HTML -
    shared by render_footer() (drawn once on every live page) and print_registry's combined
    report (so every printed section also carries it, since headless build() calls never
    go through render_footer() itself)."""
    return (
        'Copyright \u00a9 Dr. Sundar Sundaresan, Open Astro Technologies, USA. '
        'Download free from '
        '<a href="https://github.com/naturalstupid/PyJHora" target="_blank" rel="noopener noreferrer">'
        'https://github.com/naturalstupid/PyJHora</a>.'
        '<br><img src="https://visitor-badge.laobi.icu/badge?page_id=sarvajyotish-site" '
        'alt="visitor count" style="height:20px; margin-top:4px;" />'
    )

def render_footer():
    with ui.column().classes('w-full items-center gap-0.5 py-3 mt-4 border-t border-gray-300 no-print'):
        ui.html(_footer_inner_html()).classes('text-xs text-gray-600 text-center')

async def trigger_print_js(script):
  """Runs `script` (typically ending in `window.print()`), awaited DIRECTLY in the caller's current
  handler. Swallows only the expected TimeoutError that `window.print()` causes.
  Must be awaited by the caller: `await trigger_print_js(script)`.
  """
  try:
      await ui.run_javascript(script)
  except TimeoutError:
      pass
def print_button(label=None):
  """Adds a "Print / Save as PDF" button that triggers the browser's own print dialog
  (window.print(), via trigger_print_js()). The button itself is marked 'no-print'.
  """
  return ui.button(label or res_str('save_pdf_str', 'Print / Save as PDF'),
                    on_click=lambda: trigger_print_js('window.print()')) \
      .props('outlined dense').classes('text-gray-700 px-3 shrink-0 no-print')
def render_birth_details_bar(*, show_dob_tob=True, include_options_button=True, on_options_saved=None,
                              isolated=False, initial_overrides=None):
  """Draws one row of birth-detail inputs (older layout; pages normally use render_control_bar())."""
  shared_state = ensure_default_state()
  if isolated:
      state = dict(shared_state)
      if initial_overrides:
          state.update(initial_overrides)
  else:
      state = shared_state
  widgets = {}
  search_state = {"seq": 0}
  with ui.row().classes('w-full items-center gap-2 flex-wrap no-print'):
      if show_dob_tob:
          dob_input = ui.input(res_str('date_of_birth_str', 'Date of Birth'), value=state["date_dob"]).props('outlined dense')
          dob_input.on_value_change(lambda e: state.update({"date_dob": e.value}))
          tob_input = ui.input(res_str('time_of_birth_str', 'Time of Birth'), value=state["time_tob"]).props('outlined dense')
          tob_input.on_value_change(lambda e: state.update({"time_tob": e.value}))
          widgets['dob_input'] = dob_input
          widgets['tob_input'] = tob_input
      place_input = ui.input(label=res_str('place_str', 'Place'), value=state["place_name"]) \
          .props('outlined dense clearable debounce="300"').classes('w-64')
      with place_input:
          suggestion_menu = ui.menu().props('no-parent-event max-height="300px"').classes('w-64')
          with suggestion_menu:
              suggestions_column = ui.column().classes('gap-0 w-full')
      def apply_picked_place(label, lat_v, lon_v, tz_v):
          search_state["seq"] += 1
          place_input.value = label
          lat_input.value = str(lat_v); lon_input.value = str(lon_v); tz_input.value = str(tz_v)
          state.update({"place_name": label, "latitude": str(lat_v), "longitude": str(lon_v), "timezone": str(tz_v)})
          suggestion_menu.close()
      def handle_place_typed(e):
          text = (place_input.value or '').strip()
          state["place_name"] = text
          search_state["seq"] += 1
          my_seq = search_state["seq"]
          if len(text) < 2:
              suggestion_menu.close(); return
          rows = search_places_in_db(text)
          if my_seq != search_state["seq"]:
              return
          suggestions_column.clear()
          if not rows:
              suggestion_menu.close(); return
          with suggestions_column:
              for row in rows[:10]:
                  label, lat_v, lon_v, tz_v = row[0], row[1], row[2], row[3]
                  ui.item(label, on_click=lambda l=label, la=lat_v, lo=lon_v, t=tz_v: apply_picked_place(l, la, lo, t)) \
                      .classes('cursor-pointer hover:bg-gray-100')
          suggestion_menu.open()
      place_input.on_value_change(handle_place_typed)
      lat_input = ui.input(res_str('latitude_str', 'Latitude'), value=state["latitude"]).props('outlined dense').classes('w-28')
      lat_input.on_value_change(lambda e: state.update({"latitude": e.value}))
      lon_input = ui.input(res_str('longitude_str', 'Longitude'), value=state["longitude"]).props('outlined dense').classes('w-28')
      lon_input.on_value_change(lambda e: state.update({"longitude": e.value}))
      tz_input = ui.input(res_str('timezone_offset_str', 'Time Zone'), value=state["timezone"]).props('outlined dense').classes('w-24')
      tz_input.on_value_change(lambda e: state.update({"timezone": e.value}))
      widgets.update({'place_select': place_input, 'lat_input': lat_input, 'lon_input': lon_input, 'tz_input': tz_input})
      if include_options_button:
          ui.button(res_str('options_str', 'Options'), on_click=lambda: open_options_dialog(on_saved=on_options_saved)) \
              .classes('bg-gray-700 text-white font-bold')
  return widgets
def render_control_bar(*, show_dob_tob=True, include_options_button=True, on_options_saved=None,
                        isolated=False, initial_overrides=None,
                        on_calculate=None, calculate_label=None,
                        extra_fields_before=None, extra_fields_after=None):
  """Draws the common control bar of the calculation pages."""
  shared_state = ensure_default_state()
  if isolated:
      state = dict(shared_state)
      if initial_overrides:
          state.update(initial_overrides)
  else:
      state = shared_state
  widgets = {}
  search_state = {"seq": 0}
  with ui.column().classes('w-full gap-1 no-print'):
      with ui.row().classes('w-full items-center gap-1.5 flex-nowrap') as row1:
          if show_dob_tob:
              dob_input = ui.input(res_str('date_of_birth_str', 'Date of Birth'), value=state["date_dob"]).props('outlined dense').classes('w-32 shrink-0')
              dob_input.on_value_change(lambda e: state.update({"date_dob": e.value}))
              tob_input = ui.input(res_str('time_of_birth_str', 'Time of Birth'), value=state["time_tob"]).props('outlined dense').classes('w-24 shrink-0')
              tob_input.on_value_change(lambda e: state.update({"time_tob": e.value}))
              widgets['dob_input'] = dob_input
              widgets['tob_input'] = tob_input
          if extra_fields_before is not None:
              extra_fields_before()
          place_input = ui.input(label=res_str('place_str', 'Place'), value=state["place_name"]) \
              .props('outlined dense clearable debounce="300"').classes('w-48 shrink-0')
          with place_input:
              suggestion_menu = ui.menu().props('no-parent-event max-height="300px"').classes('w-64')
              with suggestion_menu:
                  suggestions_column = ui.column().classes('gap-0 w-full')
          def apply_picked_place(label, lat_v, lon_v, tz_v):
              search_state["seq"] += 1
              place_input.value = label
              lat_input.value = str(lat_v); lon_input.value = str(lon_v); tz_input.value = str(tz_v)
              state.update({"place_name": label, "latitude": str(lat_v), "longitude": str(lon_v), "timezone": str(tz_v)})
              suggestion_menu.close()
          def handle_place_typed(e):
              text = (place_input.value or '').strip()
              state["place_name"] = text
              search_state["seq"] += 1
              my_seq = search_state["seq"]
              if len(text) < 2:
                  suggestion_menu.close(); return
              rows = search_places_in_db(text)
              if my_seq != search_state["seq"]:
                  return
              suggestions_column.clear()
              if not rows:
                  suggestion_menu.close(); return
              with suggestions_column:
                  for row in rows[:10]:
                      label, lat_v, lon_v, tz_v = row[0], row[1], row[2], row[3]
                      ui.item(label, on_click=lambda l=label, la=lat_v, lo=lon_v, t=tz_v: apply_picked_place(l, la, lo, t)) \
                          .classes('cursor-pointer hover:bg-gray-100')
              suggestion_menu.open()
          place_input.on_value_change(handle_place_typed)
          lat_input = ui.input(res_str('latitude_str', 'Latitude'), value=state["latitude"]).props('outlined dense').classes('w-24 shrink-0')
          lat_input.on_value_change(lambda e: state.update({"latitude": e.value}))
          lon_input = ui.input(res_str('longitude_str', 'Longitude'), value=state["longitude"]).props('outlined dense').classes('w-24 shrink-0')
          lon_input.on_value_change(lambda e: state.update({"longitude": e.value}))
          tz_input = ui.input(res_str('timezone_offset_str', 'Time Zone'), value=state["timezone"]).props('outlined dense').classes('w-20 shrink-0')
          tz_input.on_value_change(lambda e: state.update({"timezone": e.value}))
          _gender_options = {0: res_str('gender_male_str', 'Male'), 1: res_str('gender_female_str', 'Female')}
          _gender_value = state["gender"] if state.get("gender") in _gender_options else int(const.GENDER.FEMALE)
          gender_select = ui.select(options=_gender_options, value=_gender_value, label=res_str('gender_str', 'Gender')) \
              .props('outlined dense').classes('w-28 shrink-0')
          gender_select.on_value_change(lambda e: state.update({"gender": e.value}))
          widgets.update({'place_select': place_input, 'lat_input': lat_input, 'lon_input': lon_input, 'tz_input': tz_input,
                          'gender_select': gender_select})
          if extra_fields_after is not None:
              extra_fields_after()
          if include_options_button:
              settings_button = ui.button(res_str('options_str', 'Settings'), on_click=lambda: open_options_dialog(on_saved=on_options_saved)) \
                  .props('outlined dense').classes('text-gray-700 px-3 shrink-0')
              widgets['settings_button'] = settings_button
          if on_calculate is not None:
              calculate_button = ui.button(calculate_label or res_str('compute_str', 'Calculate'), on_click=on_calculate) \
                  .props('dense').classes('bg-green-600 text-white font-bold px-3 shrink-0')
              widgets['calculate_button'] = calculate_button
          # Global "Save as PDF" button: drawn here, as the LAST button of row1, instead of its own
          # dedicated full-width row above the green nav bar (that wasted page height - moved here
          # per the user's own explicit request). Still just ONE call per page, same as before -
          # render_control_bar() itself is only ever called once per page (see each tab's own
          # build()). The local import mirrors the old navigation_header() call: print_registry
          # imports components at module level, so importing print_registry at components.py's own
          # module level would be a circular import - importing it lazily, inside this function,
          # avoids that.
          import print_registry
          print_registry.render_global_print_button()
      row2 = ui.row().classes('w-full items-center gap-1.5 flex-wrap')
  # IMPORTANT: this container is created OUTSIDE the 'w-full gap-1 no-print' column above (on
  # purpose - it is NOT nested inside row1 alongside the button). That column's own 'no-print'
  # class sets display:none on ITSELF during printing, which would also hide any descendant
  # unconditionally - no child CSS rule could then make this container visible again for the
  # combined "Save as PDF" print. See print_registry.ensure_combined_report_container()'s own
  # docstring for the full explanation.
  import print_registry
  print_registry.ensure_combined_report_container()
  fit_row(row1, add_css=False)
  fit_row(row2, add_css=False)
  widgets['row2'] = row2
  tz_sync.install(widgets)
  calc_highlight.install(widgets, hint=res_str('inputs_changed_str', 'Inputs changed - click to update the results'))
  return widgets
def render_full_panchangam_popup(jd, place_obj, ayanamsa_mode=None):
  """Opens a dialog with the full panchangam, in three columns."""
  from jhora.panchanga import info
  _KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR = 'green'
  _HEADER_FORMAT_ = '<b><span style="color:' + _HEADER_COLOR + ';">{}</span></b><br>'
  _KEY_VALUE_FORMAT_ = '<span style="color:' + _KEY_COLOR + ';">{}  </span><span style="color:' + _VALUE_COLOR + ';">{}</span><br>'
  dialog = ui.dialog()
  with dialog, ui.card().classes('w-full max-w-6xl'):
      with ui.row().classes('w-full items-center justify-between'):
          ui.label(res_str('panchangam_str','Panchangam')).classes('text-xl font-bold text-green-700')
          ui.button(icon='close', on_click=dialog.close).props('flat round dense')
      try:
          with calc_lock():
              mode = ayanamsa_mode if ayanamsa_mode is not None else const._DEFAULT_AYANAMSA_MODE
              results_dict = info.get_panchangam_resources(jd, place_obj, ayanamsa_mode=mode)
          sep_str = '<br>'
          info_str = ''.join([
              _HEADER_FORMAT_.format(k) if v.strip() == '' else _KEY_VALUE_FORMAT_.format(k, v)
              for k, v in results_dict.items()
          ])
          info_list = [ele for ele in info_str.split(sep_str) if ele.strip() != '']
          info_len = int(len(info_list) / 3)
          with ui.row().classes('w-full justify-between items-start gap-4 flex-nowrap overflow-x-auto h-[70vh]'):
              with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow overflow-y-auto h-full'):
                  ui.html(sep_str.join(info_list[:info_len]))
              with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow overflow-y-auto h-full'):
                  ui.html(sep_str.join(info_list[info_len:2 * info_len]))
              with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow overflow-y-auto h-full'):
                  ui.html(sep_str.join(info_list[2 * info_len:]))
      except Exception as e:
          ui.label(f'Error computing Panchangam: {e}').classes('text-red-600')
  dialog.open()
  return dialog

async def run_io_bound_ctx(fn, *args, **kwargs):
    """run.io_bound that keeps the visitor's context (language, settings, client)."""
    ctx = contextvars.copy_context()
    return await run.io_bound(ctx.run, fn, *args, **kwargs)

class DelayedBusyIndicator:
  """Non-intrusive "please wait" UI that only becomes visible if a worker-thread computation is still
  running after a short delay. The whole row is marked 'no-print'.
  """
  STOPPED = object()
  def __init__(self, *, buttons=None, delay=0.8, show_stop=True, stop_label=None, stop_message=None,
               on_stop=None, label_classes='font-bold text-green-700 text-sm'):
    if buttons is None:
      buttons = []
    elif not isinstance(buttons, (list, tuple)):
      buttons = [buttons]
    self._buttons = [b for b in buttons if b is not None]
    self._delay = delay
    self._gen = 0
    self._on = False
    self._stop_message = stop_message or 'Stopped.'
    self._on_stop = on_stop
    with ui.row().classes('items-center gap-2 no-print'):
      self.spinner = ui.spinner(size='sm')
      self.status_label = ui.label('').classes(label_classes)
      self.stop_button = ui.button(stop_label or 'Stop', on_click=lambda: self.stop()) \
          .props('outlined dense').classes('text-red-700 border-red-400 ml-2')
    self.spinner.set_visibility(False)
    self.status_label.set_visibility(False)
    if not show_stop:
      self.stop_button.delete()
      self.stop_button = None
    else:
      self.stop_button.set_visibility(False)
  def add_button(self, button):
    if button is not None:
      self._buttons.append(button)
  @property
  def is_busy(self):
    return self._on
  def _reveal(self, wait_text):
    self.spinner.set_visibility(True)
    self.status_label.set_text(wait_text)
    self.status_label.set_visibility(True)
    if self.stop_button is not None:
      self.stop_button.set_visibility(True)
  def _hide(self):
    self.spinner.set_visibility(False)
    self.status_label.set_visibility(False)
    if self.stop_button is not None:
      self.stop_button.set_visibility(False)
  def stop(self):
    if not self._on:
      return
    self._gen += 1
    self._on = False
    self.status_label.set_text(self._stop_message)
    if self.stop_button is not None:
      self.stop_button.set_visibility(False)
    self.spinner.set_visibility(False)
    for button in self._buttons:
      button.enable()
    if self._on_stop is not None:
      self._on_stop()
  async def run(self, fn, *args, wait_text='Please wait...', **kwargs):
    if self._on:
      return self.STOPPED
    self._gen += 1
    my_gen = self._gen
    self._on = True
    for button in self._buttons:
      button.disable()
    async def _reveal_after_delay():
      await asyncio.sleep(self._delay)
      if self._gen == my_gen and self._on:
        self._reveal(wait_text)
    reveal_task = asyncio.ensure_future(_reveal_after_delay())
    try:
      context = contextvars.copy_context()
      result = await run.io_bound(context.run, fn, *args, **kwargs)
      if self._gen != my_gen:
        return self.STOPPED
      return result
    finally:
      reveal_task.cancel()
      if self._gen == my_gen:
        self._on = False
        try:
          self._hide()
        except RuntimeError:
          pass
        for button in self._buttons:
          try:
            button.enable()
          except RuntimeError:
            pass
