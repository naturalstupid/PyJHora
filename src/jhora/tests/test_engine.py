import sys
import time
import re
import argparse
import statistics
import subprocess
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from jhora import const


# ============================================================
# CONFIG
# ============================================================

# Engines to benchmark
ENGINES = [
    "CSV_5K",
    "CSV_5K_IN",
    "PICKLE",
    "SQLITE",
]

# Number of benchmark runs per engine
RUNS_PER_ENGINE = 3

# Optional warmup runs (not included in averages)
WARMUP_RUNS = 0

# How long to keep UI open in each child run before auto-close
AUTO_CLOSE_MS = 750


# ============================================================
# ENGINE SETUP
# ============================================================
def set_engine_by_name(engine_name: str):
    engine_name = engine_name.strip().upper()

    mapping = {
        "NONE": const.PLACE_DATABASE_ENGINE.NONE,
        "CSV_5K": const.PLACE_DATABASE_ENGINE.CSV_5K,
        "CSV_5K_IN": const.PLACE_DATABASE_ENGINE.CSV_5K_IN,
        "PICKLE": const.PLACE_DATABASE_ENGINE.PICKLE,
        "SQLITE": const.PLACE_DATABASE_ENGINE.SQLITE,
    }

    if engine_name not in mapping:
        raise ValueError(f"Unknown engine name: {engine_name}")

    const.set_place_database_engine(mapping[engine_name])


# ============================================================
# CHILD MODE: RUN ONE ENGINE ONE TIME
# ============================================================
def run_one_engine_once(engine_name: str, auto_close_ms: int):
    start_time = time.time()

    def except_hook(cls, exception, traceback):
        print("exception called", flush=True)
        sys.__excepthook__(cls, exception, traceback)

    sys.excepthook = except_hook

    set_engine_by_name(engine_name)

    print(
        f"BENCHMARK_START "
        f"engine={engine_name} "
        f"file={const._place_database_file}",
        flush=True
    )

    app = QApplication(sys.argv)

    # Import here so parent benchmark process stays lighter
    from jhora.ui.horo_chart_tabs import ChartTabbed

    chart = ChartTabbed()

    # Mirror your normal startup sequence
    chart.language("English")
    chart.chart_type("South_Indian")

    t_compute_start = time.time()
    chart.compute_horoscope()
    compute_elapsed = time.time() - t_compute_start

    chart.show()

    total_to_show = time.time() - start_time

    print(
        f"BENCHMARK_RESULT "
        f"engine={engine_name} "
        f"compute={compute_elapsed:.6f} "
        f"total_to_show={total_to_show:.6f}",
        flush=True
    )

    # Auto-close the UI after a short delay
    QTimer.singleShot(auto_close_ms, app.quit)

    app.exec()

    total_until_exit = time.time() - start_time
    print(
        f"BENCHMARK_EXIT "
        f"engine={engine_name} "
        f"total_until_exit={total_until_exit:.6f}",
        flush=True
    )

    sys.stdout.flush()
    sys.stderr.flush()

    # Benchmark-only: avoid PyQt/Windows teardown crashes
    os._exit(0)


# ============================================================
# PARENT MODE: RUN ALL ENGINES IN FRESH SUBPROCESSES
# ============================================================
RESULT_RE = re.compile(
    r"BENCHMARK_RESULT.*?engine=(?P<engine>\S+).*?compute=(?P<compute>[0-9.]+).*?total_to_show=(?P<show>[0-9.]+)"
)
EXIT_RE = re.compile(
    r"BENCHMARK_EXIT.*?engine=(?P<engine>\S+).*?total_until_exit=(?P<exit>[0-9.]+)"
)


def run_subprocess_for_engine(engine_name: str, run_num: int, auto_close_ms: int):
    cmd = [
        sys.executable,
        __file__,
        "--child",
        "--engine", engine_name,
        "--autoclose-ms", str(auto_close_ms),
    ]

    print("=" * 100)
    print(f"RUN {run_num} | ENGINE={engine_name}")
    print("CMD:", " ".join(cmd), flush=True)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    stdout = proc.stdout
    stderr = proc.stderr

    print(stdout, flush=True)
    if stderr.strip():
        print("STDERR:", stderr, flush=True)

    m_result = RESULT_RE.search(stdout)
    m_exit = EXIT_RE.search(stdout)

    # IMPORTANT:
    # Accept the run if benchmark output was printed,
    # even if Qt crashes during shutdown on Windows.
    if not m_result:
        raise RuntimeError(
            f"Could not parse BENCHMARK_RESULT for engine={engine_name}, run={run_num}. "
            f"Return code was {proc.returncode}"
        )

    if proc.returncode != 0:
        print(
            f"WARNING: Non-zero return code for engine={engine_name}, run={run_num}: "
            f"{proc.returncode}. Benchmark output was captured, so continuing.",
            flush=True
        )

    compute = float(m_result.group("compute"))
    total_to_show = float(m_result.group("show"))
    total_until_exit = float(m_exit.group("exit")) if m_exit else None

    return {
        "engine": engine_name,
        "run": run_num,
        "compute": compute,
        "total_to_show": total_to_show,
        "total_until_exit": total_until_exit,
    }


def summarize(values):
    return {
        "min": min(values),
        "max": max(values),
        "avg": statistics.mean(values),
        "median": statistics.median(values),
    }


def fmt_stats(stats):
    return (
        f"min={stats['min']:.3f}s "
        f"max={stats['max']:.3f}s "
        f"avg={stats['avg']:.3f}s "
        f"median={stats['median']:.3f}s"
    )


def benchmark_all_engines():
    all_results = {}

    for engine_name in ENGINES:
        runs = []

        total_runs = WARMUP_RUNS + RUNS_PER_ENGINE
        for i in range(1, total_runs + 1):
            result = run_subprocess_for_engine(engine_name, i, AUTO_CLOSE_MS)
            runs.append(result)

        # Drop warmup runs from summary if configured
        runs_for_stats = runs[WARMUP_RUNS:] if WARMUP_RUNS > 0 else runs

        all_results[engine_name] = runs_for_stats

    print("\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)

    for engine_name, runs in all_results.items():
        compute_vals = [r["compute"] for r in runs]
        show_vals = [r["total_to_show"] for r in runs]
        exit_vals = [r["total_until_exit"] for r in runs if r["total_until_exit"] is not None]

        print(f"\nENGINE: {engine_name}")
        print("  compute_horoscope :", fmt_stats(summarize(compute_vals)))
        print("  total_to_show     :", fmt_stats(summarize(show_vals)))
        if exit_vals:
            print("  total_until_exit  :", fmt_stats(summarize(exit_vals)))

        print("  per-run:")
        for r in runs:
            if r["total_until_exit"] is not None:
                print(
                    f"    run {r['run']}: "
                    f"compute={r['compute']:.3f}s, "
                    f"total_to_show={r['total_to_show']:.3f}s, "
                    f"total_until_exit={r['total_until_exit']:.3f}s"
                )
            else:
                print(
                    f"    run {r['run']}: "
                    f"compute={r['compute']:.3f}s, "
                    f"total_to_show={r['total_to_show']:.3f}s"
                )


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true", help="Run one engine once (internal use)")
    parser.add_argument("--engine", type=str, default=None, help="Engine name for child mode")
    parser.add_argument("--autoclose-ms", type=int, default=AUTO_CLOSE_MS, help="Auto-close delay for child mode")
    args = parser.parse_args()

    if args.child:
        if not args.engine:
            raise ValueError("--engine is required in --child mode")
        run_one_engine_once(args.engine, args.autoclose_ms)
    else:
        benchmark_all_engines()


if __name__ == "__main__":
    main()