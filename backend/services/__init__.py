# Services package initialization
# Import services with error handling to allow partial imports

# Try importing ML-dependent services
try:
    from .mie_service import MIEService
    _has_mie = True
except ImportError as e:
    print(f"Warning: Could not import MIEService (ML dependencies): {e}")
    _has_mie = False

try:
    from .cit_service import CITService
    _has_cit = True
except ImportError as e:
    print(f"Warning: Could not import CITService: {e}")
    _has_cit = False

try:
    from .policy_service import PolicyService
    _has_policy = True
except ImportError as e:
    print(f"Warning: Could not import PolicyService: {e}")
    _has_policy = False

# Import live news service (no ML dependencies)
try:
    from .live_news_service import LiveNewsService, live_news_service
    _has_live_news = True
except ImportError as e:
    print(f"Warning: Could not import LiveNewsService: {e}")
    import traceback
    traceback.print_exc()
    _has_live_news = False

# Build __all__ dynamically based on what imported successfully
__all__ = []
if _has_mie:
    __all__.extend(["MIEService"])
if _has_cit:
    __all__.extend(["CITService"])
if _has_policy:
    __all__.extend(["PolicyService"])
if _has_live_news:
    __all__.extend(["LiveNewsService", "live_news_service"])