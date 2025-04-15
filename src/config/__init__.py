import os
import uuid

import yaml

LANG_CODE_MAP = {
    'English': 'en-US',
    'Hindi': 'hi-IN',
    'Tamil': 'ta-IN',
    'Gujarati': 'gu-IN',
    'Bengali': 'bn-IN',
    'Kannada': 'kn-IN',
    'Telugu': 'te-IN',
    'Spanish': 'es-ES',
}

SYSTEM_ENV_DEFAULTS = {
    "GCS_BUCKET": "gs://ithihasa",
    "GCP_PARENT_PROJECT_LOCATION": "projects/sage-ace-233407/locations/us-central1",
    "GCP_PARENT_PROJECT": "sage-ace-233407",
    "GCP_LOCATION": "us-central1",
    "VERTEX_MODEL_ID": "gemini-2.0-flash-001"
}


def set_system_env_defaults():
    for key, value in SYSTEM_ENV_DEFAULTS.items():
        if key not in os.environ:
            os.environ[key] = value


def get_base_translation_prompt():
    return f"""
        Your a lingual expert and adept at efficient and accurate translations. Given a piece of text or a verse specified in the <TEXT> field in a given language indicated by <INPUT_LANGUAGE>, translate the text into the set of languages specified as the keys of <LANGUAGE_CODE_MAP> dictionary which contains the language name and its specific code using the following guardrails: 
        - Ensure you use succinct easy to understand words for the target language in the translation. 
        - The output must only be in the set of target languages and not in the source language.
        - The output must be like a discourse which makes it easy to understand for the target audience for each language specified in the <LANGUAGE_CODE_MAP> dictionary.
        
        The output format must follow the following pattern:
        - The response must only be a valid JSON response. No other content should be returned. 
        - JSON must include 2 fields - {{"answer": {{"<language_code>": "<translated_answer>"}}}}. The answer field must be a dictionary of the language code as found in the values of <LANGUAGE_CODE_MAP>, and its corresponding translated text in that language.
        - Do not allow translations for more than 10 languages at a time in one request.  
        - Do not return with any other response format other than the json. 
        """


def get_translation_prompt(part_info, text, lang, target_langs_map):
    return get_base_translation_prompt() \
           + "\n" \
           + f"""
        <TEXT>
        {text}
        </TEXT>
        
        <INPUT_LANGUAGE>
        {lang}
        </INPUT_LANGUAGE>
        
        <LANGUAGE_CODE_MAP>
        {target_langs_map}
        </LANGUAGE_CODE_MAP
        """


def get_part_summary_for_img_prompt(text):
    return f"""
        Given the TEXT below in <TEXT> field in a given language, generate a succinct summary of the text that can be 
        used for image generation in english language. 
        The output format must follow the following pattern:
        - must be ONLY in json format
        - must only contain one field - {{"summary": "<summary>"}}. The summary field must be a succinct summary of the text in english language.
        - The summary must be in a single line and not more than 100 words.
        
        <TEXT>
        {text}
        </TEXT>
    """


def get_image_prompt(text, description):
    return f""" Generate an image based on the following text provided in <TEXT> field as a summary of a video. 
                    Include the following guardrails in your response:
                    - The image must NOT contain any text or writings or logos. 
                    - The image must be in a 16:9 aspect ratio.
                    - The image must be in a high resolution.
                    - The image must be in a format that is compatible with video editing software.
                    - The image generation leverages the broader context of the video as specified in <DESCRIPTION> field if available
                    - Generate only 1 single image. 
                    - The image must NOT contain any text/writings or logos. 
                    - Image format must be in png format. 

                    <TEXT>
                    {text}
                    </TEXT>

                    <DESCRIPTION>
                    {description}
                    </DESCRIPTION>
                """


PLATFORMS = {
    "audio": ["youtube", "soundcloud", "spotify", "apple_podcasts", "google_podcasts"],
    "video": ["youtube", "vimeo"]
}


class ContentConfig:
    def __init__(self, name, id, source_path, source_type, source_lang, background_music, translations,
                 publishing_platforms,
                 generate_ai_description, generate_milestones, split_into_parts, from_chunk):
        self.name = name
        self.id = id
        self.source_path = source_path
        self.content_type = source_type
        self.source_language = source_lang
        self.background_music = background_music
        self.translations = translations
        self.publishing_platforms = publishing_platforms
        self.generate_ai_description = generate_ai_description
        self.generate_milestones = generate_milestones
        self.split_into_parts = split_into_parts
        self.from_chunk = from_chunk
        self.validate_translations()
        self.validate_publishing_platforms()
        set_system_env_defaults()

    def validate_publishing_platforms(self):
        for platform in self.publishing_platforms:
            if str(platform).lower() not in PLATFORMS[self.content_type]:
                raise ValueError(f"Invalid publishing platform: {platform}")

    def validate_translations(self):
        for translation in self.translations:
            if translation not in LANG_CODE_MAP:
                raise ValueError(f"Invalid translation language: {translation}")

    @classmethod
    def from_dict(cls, data):
        bg_music = data.get('background_music').get('path') if data.get('background_music') else None
        return cls(
            name=data['name'],
            id=data.get('id', uuid.uuid4()),
            source_path=data['source']['path'],
            source_type=data['content_type'],
            source_lang=data['source']['language'],
            background_music=bg_music,
            translations=data['translations'],
            publishing_platforms=data['publishing_platforms'],
            generate_ai_description=data['generate_ai_description'],
            generate_milestones=data['generate_milestones'],
            split_into_parts=data['split_into_parts'],
            from_chunk=data.get('from_chunk', 0)
        )


def parse_config(config_path):
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    content_config = ContentConfig.from_dict(config_data['content_manifest'])
    return content_config
