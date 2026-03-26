"""Tool API client libraries.

Each client extends BaseAPIClient with tool-specific authentication,
endpoint mappings, and response parsing.
"""

from scripts.api_clients.base_client import (
    APIError,
    AuthenticationError,
    BaseAPIClient,
    RateLimitError,
)
from scripts.api_clients.canvas_client import CanvasClient
from scripts.api_clients.elevenlabs_client import ElevenLabsClient
from scripts.api_clients.gamma_client import GammaClient
from scripts.api_clients.panopto_client import PanoptoClient
from scripts.api_clients.qualtrics_client import QualtricsClient

__all__ = [
    "APIError",
    "AuthenticationError",
    "BaseAPIClient",
    "CanvasClient",
    "ElevenLabsClient",
    "GammaClient",
    "PanoptoClient",
    "QualtricsClient",
    "RateLimitError",
]
