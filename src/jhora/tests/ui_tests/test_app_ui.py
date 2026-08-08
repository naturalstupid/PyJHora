# test_app_ui.py

import unittest
from PyQt6 import QtCore, QtWidgets
from jhora.tests.ui_tests.test_helpers import (
    BaseUITestCase,
    log,
    wait,
    close_visible_menus,
    close_active_modal_dialog_if_any,
    _CHECK_STATS,
    _write_line,
    _STOP_ON_FAIL
)

class SharedAppRunner(BaseUITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Open the window ONCE for the entire suite
        from jhora.ui.horo_chart_tabs import ChartTabbed
        cls._shared_window = ChartTabbed()
        cls._shared_window.date_of_birth("1996,12,7")
        cls._shared_window.time_of_birth("10:34:00")
        cls._shared_window.place('Chennai,India',13.0878,80.2785,5.5)
        cls._shared_window.show()
        cls._shared_window.compute_horoscope()
        QtWidgets.QApplication.processEvents()

    def setUp(self):
        self.main_window = self.__class__._shared_window

        # --- CRITICAL: CLEAR SLATE BEFORE EVERY TAB TEST ---
        log("[RUNNER] Purging lingering UI states and event queue...")

        # 1. Close any active popup menus or tooltips left open
        while QtWidgets.QApplication.activePopupWidget():
            popup = QtWidgets.QApplication.activePopupWidget()
            popup.close()

        # 2. Close any lingering top-level modal dialogs except the main app window
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget != self.main_window and widget.isVisible():
                log(f"[RUNNER] Force closing lingering window: {type(widget).__name__}")
                widget.close()

        # 3. Flush the event loop to ensure all deferred deletions finish processing
        QtWidgets.QApplication.processEvents()

        # 4. Force fully reactivate and pull the main window back to foreground focus
        self.main_window.activateWindow()
        self.main_window.raise_()
        QtWidgets.QApplication.processEvents()
        wait(500)

    # ---------------------------------------------------------
    # HARD RESET between _run_tab_* calls
    # ---------------------------------------------------------
    def _reset_app_state(self):
        """
        Hard reset between tab test runs.
        Closes any menus/dialogs left open and restores focus to main window.
        Uses only functions available in test_helpers.
        """
        log("[RUNNER] _reset_app_state: cleaning up between tabs...")
        close_visible_menus()
        close_active_modal_dialog_if_any()

        while QtWidgets.QApplication.activePopupWidget():
            QtWidgets.QApplication.activePopupWidget().close()

        QtWidgets.QApplication.processEvents()
        self.main_window.activateWindow()
        self.main_window.raise_()
        QtWidgets.QApplication.processEvents()
        wait(400)

    # ---------------------------------------------------------
    # INTERNAL EXECUTION METHODS
    # ---------------------------------------------------------
    def _run_tab_switching(self):
        test_name = "Tab Switching"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_tab_switching import TestTabSwitching
        t = TestTabSwitching()
        t.main_window = self.main_window
        TestTabSwitching.test_compute_then_switch_all_tabs(t)
        TestTabSwitching.test_tab_titles_exist_after_compute(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")
        
        ######### Always Reset Application State
        self._reset_app_state()
        
    def _run_tab_panchanga(self):
        test_name = "Tab Panchanga"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_panchanga_tab import TestPanchangaTab
        t = TestPanchangaTab()
        t.main_window = self.main_window
        TestPanchangaTab.test_panchanga_place_and_compute(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_bhava(self):
        test_name = "Tab Bhava"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_bhava_tab import TestBhavaTab
        t = TestBhavaTab()
        t.main_window = self.main_window
        TestBhavaTab.test_bhava_tab_defaults_and_updates(t)
        TestBhavaTab.test_bhava_chart_options_button_opens_dialog(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_chart(self):
        test_name = "Tab Chart"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_chart_tab import TestChartTab
        t = TestChartTab()
        t.main_window = self.main_window
        TestChartTab.test_chart_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_chakra(self):
        test_name = "Tab Chakra"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_chakra_tab import TestChakraTab
        t = TestChakraTab()
        t.main_window = self.main_window
        TestChakraTab.test_chakra_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_kpinfo(self):
        test_name = "Tab KP-Info"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_kpinfo_tab import TestKpInfoTab
        t = TestKpInfoTab()
        t.main_window = self.main_window
        TestKpInfoTab.test_kp_info_tab_all_indices(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_saham(self):
        test_name = "Tab Saham"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_saham_tab import TestSahamTab
        t = TestSahamTab()
        t.main_window = self.main_window
        TestSahamTab.test_saham_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_sphuta(self):
        test_name = "Tab Sphuta"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_sphuta_tab import TestSphutaTab
        t = TestSphutaTab()
        t.main_window = self.main_window
        TestSphutaTab.test_sphuta_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_amsa(self):
        test_name = "Tab Amsa Rulers"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_amsa_tab import TestAmsaTab
        t = TestAmsaTab()
        t.main_window = self.main_window
        TestAmsaTab.test_amsa_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_drishti(self):
        test_name = "Tab Graha/Raasi Drishti: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_drishti_tab import TestDrishtiTab
        t = TestDrishtiTab()
        t.main_window = self.main_window
        TestDrishtiTab.test_drishti_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_arudha(self):
        test_name = "Tab Graha/Bhaava Arudha: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_arudha_tab import TestArudhaTab
        t = TestArudhaTab()
        t.main_window = self.main_window
        TestArudhaTab.test_arudha_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_ashtaka_varga(self):
        test_name = "Tab Ashtakavarga: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_ashtaka_tab import TestAshtakaTab
        t = TestAshtakaTab()
        t.main_window = self.main_window
        TestAshtakaTab.test_ashtaka_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_argala(self):
        test_name = "Tab Argala Virodhargala: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_argala_tab import TestArgalaTab
        t = TestArgalaTab()
        t.main_window = self.main_window
        TestArgalaTab.test_argala_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_shodhaya(self):
        test_name = "Tab Shodhaya Pindam: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_shodhaya_tab import TestShodhayaTab
        t = TestShodhayaTab()
        t.main_window = self.main_window
        TestShodhayaTab.test_shodhaya_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_dasha(self):
        test_name = "Tab Dasha Bhukthi"
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_dhasa_tab import TestDashasTab
        t = TestDashasTab()
        t.main_window = self.main_window
        TestDashasTab.test_dashas_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_yoga(self):
        test_name = "Tab Yoga: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_yoga_tab import TestYogaTab
        t = TestYogaTab()
        t.main_window = self.main_window
        TestYogaTab.test_yoga_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_dosha(self):
        test_name = "Tab Dosha: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_dosha_tab import TestDoshaTab
        t = TestDoshaTab()
        t.main_window = self.main_window
        TestDoshaTab.test_dosha_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_prediction(self):
        test_name = "Tab Predictions: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_prediction_tab import TestPredictionTab
        t = TestPredictionTab()
        t.main_window = self.main_window
        TestPredictionTab.test_prediction_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    def _run_tab_compatibility(self):
        test_name = "Tab Compatibility: "
        start_test_no = _CHECK_STATS["checks_run"]
        start_pass_no = _CHECK_STATS["checks_passed"]
        log(f">>> Running: {test_name} <<<")
        from jhora.tests.ui_tests.test_compatibility_tab import TestCompatibilityTab
        t = TestCompatibilityTab()
        t.main_window = self.main_window
        TestCompatibilityTab.test_compatibility_tab_comprehensive(t)
        total_tests = _CHECK_STATS["checks_run"] - start_test_no
        passed_tests = _CHECK_STATS["checks_passed"] - start_pass_no
        _write_line(f">>> CHECK-SUMMARY {test_name} Stats: Total:{total_tests} Passed:{passed_tests}")

        ######### Always Reset Application State
        self._reset_app_state()

    # ---------------------------------------------------------
    # MAIN EXECUTOR
    # ---------------------------------------------------------
    def test_orchestrator(self):
        """Single clean entry point that executes the entire suite sequentially."""
        _STOP_ON_FAIL = False
        _PARTIAL_RUN = False

        if _PARTIAL_RUN:
            log("=== STARTING PARTIAL AUTOMATION SUITE ===")
            self._run_tab_dasha()
        else:
            log("=== STARTING FULL APPLICATION AUTOMATION SUITE ===")
            self._run_tab_switching()

            self._run_tab_panchanga()

            self._run_tab_bhava()

            self._run_tab_chart()

            self._run_tab_kpinfo()

            self._run_tab_chakra()

            self._run_tab_amsa()

            self._run_tab_sphuta()

            self._run_tab_saham()
            
            self._run_tab_drishti()

            self._run_tab_arudha()

            self._run_tab_ashtaka_varga()

            self._run_tab_argala()

            self._run_tab_shodhaya()

            self._run_tab_yoga()

            self._run_tab_dosha()

            self._run_tab_prediction()

            self._run_tab_compatibility()

            self._run_tab_dasha()

        log("=== ALL TEST TABS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    unittest.main()
