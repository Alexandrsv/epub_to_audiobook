from openai import OpenAI

from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.tts_providers.openai_tts_provider import OpenAITTSProvider


SILERO_DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
SILERO_DEFAULT_MODEL = "v5_5_ru"
SILERO_DEFAULT_VOICE = "eugene"
SILERO_PARAGRAPH_MARKER = " @BRK# "


def get_silero_supported_models():
    return [SILERO_DEFAULT_MODEL]


def get_silero_supported_voices():
    return ["aidar", "baya", "kseniya", "xenia", "eugene"]


class SileroTTSProvider(OpenAITTSProvider):
    """OpenAI-compatible client for the separately running Silero service."""

    def __init__(self, config: GeneralConfig):
        config.silero_base_url = config.silero_base_url or SILERO_DEFAULT_BASE_URL
        config.model_name = config.model_name or SILERO_DEFAULT_MODEL
        config.voice_name = config.voice_name or SILERO_DEFAULT_VOICE
        config.language = "ru"
        config.output_format = config.output_format or "mp3"
        config.speed = config.speed or 1.0
        config.instructions = None
        super().__init__(config)

    def create_client(self):
        return OpenAI(
            base_url=self.config.silero_base_url,
            api_key="silero-local",
            max_retries=4,
        )

    def get_model_price(self, model):
        return 0.0

    def get_max_chars(self):
        # Paragraph markers must reach the service intact. The service performs
        # normalization and the model-specific 140-character chunking.
        return 1_000_000

    def get_break_string(self):
        return SILERO_PARAGRAPH_MARKER
