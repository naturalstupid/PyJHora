from . import config as _config
# Load config-backed runtime settings once, automatically,
# whenever the jhora package is imported.
_config.initialize_runtime    