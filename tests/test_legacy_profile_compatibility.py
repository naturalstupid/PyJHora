"""Lifecycle and scope checks for the optional legacy backend; no private data."""
import io
import hashlib
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from jhora import const, utils
from jhora.panchanga import drik
from jhora.compatibility import jhora8


class FakeProcess:
    def __init__(self, output='{"ready":true}\n'):
        self.stdin = io.StringIO()
        self.stdout = io.StringIO(output)
        self.stderr = io.StringIO()
        self.returncode = None
        self.terminated = False

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.returncode = 0
        return 0

    def terminate(self):
        self.terminated = True
        self.returncode = -1


class LegacyProfileTests(unittest.TestCase):
    def test_state_restores_even_when_worker_cleanup_raises(self):
        saved = (drik.ascendant, drik.sunrise, drik.planet_list, const._DEFAULT_AYANAMSA_MODE)
        backend = Mock()
        backend.close.side_effect = RuntimeError('cleanup failed')
        with patch.object(jhora8, 'LegacySwiss', return_value=backend):
            with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                with jhora8._export_profile():
                    pass
        self.assertEqual(saved, (drik.ascendant, drik.sunrise, drik.planet_list, const._DEFAULT_AYANAMSA_MODE))

    def test_configuration_failure_happens_before_worker_creation(self):
        with patch.object(const, 'set_node_mode', side_effect=ValueError('configuration failed')), \
             patch.object(jhora8, 'LegacySwiss') as worker:
            with self.assertRaisesRegex(ValueError, 'configuration failed'):
                jhora8._install(drik, drik.swe)
            worker.assert_not_called()

    def test_startup_timeout_terminates_a_silent_worker(self):
        released = threading.Event()
        class SilentOutput:
            closed = False
            def __iter__(self):
                return self
            def __next__(self):
                released.wait(5)
                raise StopIteration
            def close(self):
                self.closed = True
                released.set()
        process = FakeProcess()
        process.stdout = SilentOutput()
        def terminate():
            process.terminated = True
            process.returncode = -1
            released.set()
        process.terminate = terminate
        started = time.monotonic()
        with patch.object(sys, 'platform', 'win32'), \
             patch.object(jhora8.subprocess, 'Popen', return_value=process):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                jhora8.LegacySwiss(worker_timeout=.02)
        self.assertTrue(process.terminated)
        self.assertLess(time.monotonic() - started, 2)

    def test_unsupported_platform_fails_without_launching(self):
        with patch.object(sys, 'platform', 'linux'), \
             patch.object(jhora8.subprocess, 'Popen', side_effect=AssertionError('launch attempted')):
            with self.assertRaisesRegex(RuntimeError, 'Windows'):
                jhora8.LegacySwiss()

    def test_failed_handshake_terminates_and_closes_the_worker(self):
        process = FakeProcess('invalid-json\n')
        with patch.object(sys, 'platform', 'win32'), \
             patch.object(jhora8.subprocess, 'Popen', return_value=process):
            with self.assertRaises(RuntimeError):
                jhora8.LegacySwiss()
        self.assertTrue(process.terminated)
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    def test_close_releases_all_pipes_and_exit_handler(self):
        process = FakeProcess()
        with patch.object(sys, 'platform', 'win32'), \
             patch.object(jhora8.subprocess, 'Popen', return_value=process), \
             patch.object(jhora8.atexit, 'register'), \
             patch.object(jhora8.atexit, 'unregister') as unregister:
            backend = jhora8.LegacySwiss()
            backend.close()
            backend.close()  # safe to close twice
            unregister.assert_called()
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    def test_custom_ayanamsa_is_rejected_before_any_state_change(self):
        context = getattr(jhora8, '_export_profile', getattr(jhora8, 'profile', None))
        saved_ascendant = drik.ascendant
        with patch.object(const, '_DEFAULT_AYANAMSA_MODE', 'SIDM_USER'), \
             patch.object(jhora8, 'LegacySwiss', side_effect=AssertionError('launch attempted')):
            with self.assertRaisesRegex(ValueError, 'custom ayanamsa'):
                with context():
                    pass
            self.assertEqual(const._DEFAULT_AYANAMSA_MODE, 'SIDM_USER')
        self.assertIs(drik.ascendant, saved_ascendant)

    def test_transport_eof_is_a_bounded_error(self):
        process = FakeProcess()
        with patch.object(sys, 'platform', 'win32'), \
             patch.object(jhora8.subprocess, 'Popen', return_value=process):
            backend = jhora8.LegacySwiss()
            try:
                with self.assertRaisesRegex(RuntimeError, 'terminated'):
                    backend.call('position', ut=2451545, planet=0, flags=2)
            finally:
                backend.close()


def verified_legacy_installation():
    if sys.platform != 'win32':
        return False
    dll = Path(r'C:\Program Files (x86)\Jagannatha Hora\bin\swedll32.dll')
    return dll.is_file() and hashlib.sha256(dll.read_bytes()).hexdigest() == \
        'd56ba3a6158fcec3921774b5c9fcc533374413d7b77cdbc6b83ffa082d260a69'


@unittest.skipUnless(verified_legacy_installation(), 'Verified optional JHora 8.0 DLL unavailable')
class RealLegacyProfileTests(unittest.TestCase):
    def test_synthetic_export_is_offline_and_restores_the_normal_api(self):
        from jhora.compatibility.export import export_chart
        before = (drik.ascendant, drik.sunrise, drik.sunset, const._DEFAULT_AYANAMSA_MODE)
        with patch('socket.socket.connect', side_effect=AssertionError('network attempted')):
            result = export_chart((2000, 1, 1), (12, 0, 0), 0, 0, 0,
                                  dasha_windows=(('Rahu',), ('Rahu', 'Venus')))
        self.assertEqual(len(result['positions']), 56)
        self.assertEqual(len(result['columns']), 25)
        self.assertEqual(len(result['vimshottari']), 27)
        self.assertTrue(all(0 <= value < 360 for value in result['positions'].values()))
        self.assertEqual(before, (drik.ascendant, drik.sunrise, drik.sunset, const._DEFAULT_AYANAMSA_MODE))

    def test_native_pre_dawn_events_are_internal_vedic_day_events(self):
        from jhora.compatibility.export import export_chart
        result = export_chart((2000, 1, 2), (4, 0, 0), 0, 0, 0)
        self.assertEqual(result['panchanga']['vedic_weekday'], 'Saturday')
        self.assertEqual(utils.jd_to_gregorian(result['sunrise'][2])[:3], (2000, 1, 1))

    def test_special_lagna_continuity_selects_the_birth_sun(self):
        place = drik.Place('Synthetic', 0, 0, 0, elevation=0)
        jd = utils.julian_day_number(drik.Date(2000, 1, 1), (12, 0, 0))
        with jhora8._export_profile():
            at_rise = drik.hora_lagna(jd, place, special_lagna_continuity=False)
            at_birth = drik.hora_lagna(jd, place, special_lagna_continuity=True)
        difference = (at_birth[0]*30+at_birth[1]) - (at_rise[0]*30+at_rise[1])
        self.assertGreater(abs(difference), .1)

    def test_exporter_uses_its_fixed_varnada_method(self):
        from jhora.compatibility.export import export_chart
        with patch.object(const, 'varnada_method_default', const.VARNADA_METHOD.SANJAY_RATH):
            result = export_chart((2000, 1, 1), (12, 0, 0), 0, 0, 0)
        self.assertEqual(len(result['divisionals']['Varnada Lagna']), 25)


if __name__ == '__main__':
    unittest.main()
