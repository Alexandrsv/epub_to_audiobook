import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from ebooklib import epub
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.core.audiobook_generator import AudiobookGenerator


SILERO_E2E_BASE_URL = os.environ.get("SILERO_E2E_BASE_URL")


@unittest.skipUnless(
    SILERO_E2E_BASE_URL,
    "Set SILERO_E2E_BASE_URL to run the EPUB-to-Silero integration test",
)
class SileroE2ETest(unittest.TestCase):
    def test_epub_to_tagged_mp3(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            epub_path = temp_path / "book.epub"
            output_path = temp_path / "output"
            self._write_epub(epub_path)

            config = GeneralConfig(
                SimpleNamespace(
                    input_file=str(epub_path),
                    output_folder=str(output_path),
                    preview=False,
                    output_text=True,
                    log="INFO",
                    no_prompt=True,
                    worker_count=1,
                    use_pydub_merge=False,
                    title_mode="auto",
                    newline_mode="single",
                    chapter_start=1,
                    chapter_end=1,
                    remove_endnotes=False,
                    remove_reference_numbers=False,
                    search_and_replace_file="",
                    tts="silero",
                    language="ru",
                    voice_name="eugene",
                    output_format="mp3",
                    model_name=os.environ.get("SILERO_E2E_MODEL", "v5_5_ru"),
                    speed=1.0,
                    instructions=None,
                    silero_base_url=SILERO_E2E_BASE_URL,
                )
            )
            config.log_file = temp_path / "test.log"
            AudiobookGenerator(config).run()

            mp3_path = next(output_path.glob("*.mp3"))
            text_path = next(output_path.glob("*.txt"))
            tags = ID3(mp3_path)

            self.assertGreater(MP3(mp3_path).info.length, 0)
            self.assertEqual(str(tags["TPE1"]), "Тестовый автор")
            self.assertEqual(str(tags["TALB"]), "Тестовая книга")
            self.assertEqual(str(tags["TRCK"]), "1")
            self.assertIn("123", text_path.read_text(encoding="utf-8"))
            self.assertNotIn("сто двадцать", text_path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_epub(path: Path):
        book = epub.EpubBook()
        book.set_identifier("silero-e2e")
        book.set_title("Тестовая книга")
        book.set_language("ru")
        book.add_author("Тестовый автор")
        chapter = epub.EpubHtml(
            title="Глава первая",
            file_name="chapter.xhtml",
            lang="ru",
        )
        chapter.content = (
            "<h1>Глава первая</h1>\n"
            "<p>Первый абзац содержит число 123.</p>\n"
            "<p>Второй абзац начинается здесь.</p>"
        )
        book.add_item(chapter)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.toc = (chapter,)
        book.spine = ["nav", chapter]
        epub.write_epub(str(path), book)


if __name__ == "__main__":
    unittest.main()
