import io
import logging
import math
import tempfile
import os
from pydub import AudioSegment

from openai import OpenAI

from audiobook_generator.core.audio_tags import AudioTags
from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.utils.utils import split_text, set_audio_tags, merge_audio_segments
from audiobook_generator.tts_providers.base_tts_provider import BaseTTSProvider


logger = logging.getLogger(__name__)


def get_openai_supported_output_formats():
    return ["mp3", "aac", "flac", "opus", "wav"]

def get_openai_supported_voices():
    return ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]

def get_openai_supported_models():
    return ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"]

def get_openai_instructions_example():
    return """Voice Affect: Calm, composed, and reassuring. Competent and in control, instilling trust.
Tone: Sincere, empathetic, with genuine concern for the customer and understanding of the situation.
Pacing: Slower during the apology to allow for clarity and processing. Faster when offering solutions to signal action and resolution.
Emotions: Calm reassurance, empathy, and gratitude.
Pronunciation: Clear, precise: Ensures clarity, especially with key details. Focus on key words like 'refund' and 'patience.' 
Pauses: Before and after the apology to give space for processing the apology."""

def get_price(model):
    # https://platform.openai.com/docs/pricing#transcription-and-speech-generation
    if model == "tts-1": # $15 per 1 mil chars
        return 0.015
    elif model == "tts-1-hd": # $30 per 1 mil chars
        return 0.03
    elif model == "gpt-4o-mini-tts": # $12 per 1 mil tokens (not chars, as 1 token is ~4 chars)
        return 0.003 # TODO: this could be very wrong for Chinese. Not sure how openai calculates the audio token count.
    else:
        logger.warning(f"OpenAI: Unsupported model name: {model}, unable to retrieve the price")
        return 0.0


class OpenAITTSProvider(BaseTTSProvider):
    def __init__(self, config: GeneralConfig):
        config.model_name = config.model_name or "gpt-4o-mini-tts" # default to this model as it's the cheapest
        config.voice_name = config.voice_name or "alloy"
        config.speed = config.speed or 1.0
        config.instructions = config.instructions or None
        config.output_format = config.output_format or "mp3"

        self.price = self.get_model_price(config.model_name)
        super().__init__(config)

        self.client = self.create_client()

    def create_client(self):
        # User should set OPENAI_API_KEY environment variable.
        return OpenAI(max_retries=4)

    def get_model_price(self, model):
        return get_price(model)

    def get_max_chars(self):
        # The max input is 2000 tokens for gpt-4o-mini-tts. Keep a
        # conservative character limit, especially for non-English text.
        return 1800

    def __str__(self) -> str:
        return super().__str__()

    def text_to_speech(self, text: str, output_file: str, audio_tags: AudioTags):
        text_chunks = split_text(text, self.get_max_chars(), self.config.language)

        audio_segments = []
        chunk_ids = []

        for i, chunk in enumerate(text_chunks, 1):
            chunk_id = f"chapter-{audio_tags.idx}_{audio_tags.title}_chunk_{i}_of_{len(text_chunks)}"
            logger.info(
                f"Processing {chunk_id}, length={len(chunk)}"
            )
            logger.debug(
                f"Processing {chunk_id}, length={len(chunk)}, text=[{chunk}]"
            )

            # NO retry for OpenAI TTS because SDK has built-in retry logic
            response = self.client.audio.speech.create(
                model=self.config.model_name,
                voice=self.config.voice_name,
                speed=self.config.speed,
                instructions=self.config.instructions,
                input=chunk,
                response_format=self.config.output_format,
            )

            # Log response details
            logger.debug(f"Remote server response: status_code={response.response.status_code}, "
                         f"size={len(response.content)} bytes, "
                         f"content={response.content[:128]}...")

            audio_segments.append(io.BytesIO(response.content))
            chunk_ids.append(chunk_id)

        # Use utility function to merge audio segments
        merge_audio_segments(audio_segments, output_file, self.config.output_format, chunk_ids, self.config.use_pydub_merge)

        set_audio_tags(output_file, audio_tags)

    def get_break_string(self):
        return "   "

    def get_output_file_extension(self):
        return self.config.output_format

    def validate_config(self):
        if self.config.output_format not in get_openai_supported_output_formats():
            raise ValueError(f"OpenAI: Unsupported output format: {self.config.output_format}")
        if self.config.speed < 0.25 or self.config.speed > 4.0:
            raise ValueError(f"OpenAI: Unsupported speed: {self.config.speed}")
        if self.config.instructions and len(self.config.instructions) > 0 and self.config.model_name != "gpt-4o-mini-tts":
            raise ValueError(f"OpenAI: Instructions are only supported for 'gpt-4o-mini-tts' model")

    def estimate_cost(self, total_chars):
        return math.ceil(total_chars / 1000) * self.price
