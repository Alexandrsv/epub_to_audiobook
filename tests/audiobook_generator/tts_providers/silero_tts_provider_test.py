import os
import unittest
from unittest.mock import MagicMock, patch

from audiobook_generator.core.audio_tags import AudioTags
from audiobook_generator.tts_providers.silero_tts_provider import (
    SILERO_DEFAULT_BASE_URL,
    SILERO_DEFAULT_MODEL,
    SILERO_DEFAULT_VOICE,
    SILERO_PARAGRAPH_MARKER,
    SileroTTSProvider,
    get_silero_supported_models,
)
from tests.test_utils import get_silero_config


class TestSileroTtsProvider(unittest.TestCase):
    def test_defaults_do_not_require_openai_environment(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = SileroTTSProvider(get_silero_config())

        self.assertEqual(provider.config.silero_base_url, SILERO_DEFAULT_BASE_URL)
        self.assertEqual(provider.config.model_name, SILERO_DEFAULT_MODEL)
        self.assertEqual(provider.config.voice_name, SILERO_DEFAULT_VOICE)
        self.assertEqual(provider.config.language, "ru")
        self.assertEqual(provider.config.output_format, "mp3")
        self.assertEqual(provider.estimate_cost(1_000_000), 0)
        self.assertEqual(provider.get_break_string(), SILERO_PARAGRAPH_MARKER)
        self.assertEqual(str(provider.client.base_url), f"{SILERO_DEFAULT_BASE_URL}/")
        self.assertEqual(get_silero_supported_models(), [SILERO_DEFAULT_MODEL])

    @patch(
        "audiobook_generator.tts_providers.openai_tts_provider.set_audio_tags"
    )
    @patch(
        "audiobook_generator.tts_providers.openai_tts_provider.merge_audio_segments"
    )
    def test_sends_paragraph_marker_in_one_api_request(self, merge, _set_tags):
        provider = SileroTTSProvider(get_silero_config())
        response = MagicMock()
        response.content = b"mp3"
        response.response.status_code = 200
        provider.client.audio.speech.create = MagicMock(return_value=response)
        text = f"Первый абзац.{SILERO_PARAGRAPH_MARKER}Второй абзац."

        provider.text_to_speech(
            text,
            "unused.mp3",
            AudioTags("Chapter", "Author", "Book", 1),
        )

        provider.client.audio.speech.create.assert_called_once()
        request = provider.client.audio.speech.create.call_args.kwargs
        self.assertIn("@BRK#", request["input"])
        self.assertEqual(request["model"], SILERO_DEFAULT_MODEL)
        self.assertEqual(request["voice"], SILERO_DEFAULT_VOICE)
        merge.assert_called_once()

    def test_ui_contains_license_links(self):
        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "audiobook_generator",
            "ui",
            "web_ui.py",
        )
        with open(os.path.abspath(ui_path), encoding="utf-8") as ui_file:
            source = ui_file.read()

        self.assertIn("silero-models/blob/master/LICENSE", source)
        self.assertIn("github.com/snakers4/silero-models", source)
        self.assertIn("CC BY-NC", source)
        self.assertIn("supports Russian text only", source)


if __name__ == "__main__":
    unittest.main()
