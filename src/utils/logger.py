import logging
import sys
from .config import settings

# Create logger
logger = logging.getLogger("research_brief_generator")
logger.setLevel(getattr(logging, settings.log_level.upper()))

# Create console handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(getattr(logging, settings.log_level.upper()))

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

# Export logger
__all__ = ['logger']