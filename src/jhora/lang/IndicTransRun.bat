@echo off
rem ---- One-time setup: creates the IndicTrans2 environment only if it doesn't exist yet ----
if not exist C:\venvs\indictrans\Scripts\python.exe (
    echo Creating IndicTrans2 environment...
    python -m venv --system-site-packages C:\venvs\indictrans
    C:\venvs\indictrans\Scripts\python -m pip install "transformers>=4.40,<5"
)

rem ---- Run the translation with that environment's Python ----
cd /d C:\LaptopBackup\Local\Personal\GitHub\PySSHora\src\jhora\lang
C:\venvs\indictrans\Scripts\python indic_translate_using_huggingface.py
pause
