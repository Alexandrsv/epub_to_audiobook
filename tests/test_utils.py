from types import SimpleNamespace
from audiobook_generator.config.general_config import GeneralConfig


def get_azure_config():
    args = SimpleNamespace(
        input_file='examples/The_Life_and_Adventures_of_Robinson_Crusoe.epub',
        output_folder='output',
        preview=False,
        output_text=False,
        no_prompt=True,
        worker_count=1,
        use_pydub_merge=False,
        title_mode='auto',
        log='INFO',
        newline_mode='double',
        chapter_start=1,
        chapter_end=-1,
        remove_endnotes=False,
        remove_reference_numbers=False,
        search_and_replace_file='',
        tts='azure',
        language='en-US',
        voice_name='en-US-GuyNeural',
        output_format='audio-24khz-48kbitrate-mono-mp3',
        model_name='',
        break_duration='1250'
    )
    return GeneralConfig(args)


def get_openai_config():
    args = SimpleNamespace(
        input_file='examples/The_Life_and_Adventures_of_Robinson_Crusoe.epub',
        output_folder='output',
        preview=False,
        output_text=False,
        no_prompt=True,
        worker_count=1,
        use_pydub_merge=False,
        title_mode='auto',
        log='INFO',
        newline_mode='double',
        chapter_start=1,
        chapter_end=-1,
        remove_endnotes=False,
        remove_reference_numbers=False,
        search_and_replace_file='',
        tts='openai',
        language='en-US',
        voice_name='echo',
        output_format='mp3',
        model_name='tts-1',
        speed=1.0,
        instructions=None,
    )
    return GeneralConfig(args)


def get_silero_config():
    args = SimpleNamespace(
        input_file='examples/The_Life_and_Adventures_of_Robinson_Crusoe.epub',
        output_folder='output',
        preview=False,
        output_text=False,
        log='INFO',
        newline_mode='double',
        chapter_start=1,
        chapter_end=-1,
        remove_endnotes=False,
        remove_reference_numbers=False,
        search_and_replace_file='',
        worker_count=1,
        use_pydub_merge=False,
        no_prompt=True,
        title_mode='auto',
        tts='silero',
        language=None,
        voice_name=None,
        output_format=None,
        model_name=None,
        speed=None,
        instructions=None,
        silero_base_url=None,
    )
    return GeneralConfig(args)
