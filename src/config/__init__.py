import os

import yaml

LANG_CODE_MAP = {
    'English': 'en-US',
    'Hindi': 'hi-IN',
    'Tamil': 'ta-IN',
    'Gujarati': 'gu-IN',
    'Bengali': 'bn-IN',
    'Kannada': 'kn-IN',
    'Telugu': 'te-IN'
}

SYSTEM_ENV_DEFAULTS = {
    "GCS_BUCKET": "gs://hyperion-graph-bench/mahabharat",
    "GCP_PARENT_PROJECT_LOCATION": "projects/prisma-cortex-playground/locations/us-central1",
    "GCP_PARENT_PROJECT": "prisma-cortex-playground",
    "GCP_LOCATION": "us-central1",
    "VERTEX_MODEL_ID": "gemini-2.0-flash-001"
}


def set_system_env_defaults():
    for key, value in SYSTEM_ENV_DEFAULTS.items():
        if key not in os.environ:
            os.environ[key] = value


def get_base_translation_prompt():
    return f"""
        Your a lingual expert and adept at efficient and accurate translations. Given a piece of text or a verse specified in the <TEXT> field in a given language indicated by <INPUT_LANGUAGE>, translate the text line by line into the set of languages specified in the <LANGUAGE_CODE_MAP> dictionary which contains the language and its specific language code using the following guardrails: 
        - Ensure you use succinct easy to understand words for the target language in the translation. 
        - If you see numbers written in english to track paras or verses, please remove the numbers and perform the translation. 
        - If the context is too vast, try to use memory collected from previous sessions to apply to this context. 
        - If concept is difficult, add in a simple example to illustrate the point made in the text in the target language. 
        - The translation should be engaging for an offline/podcast hearing. 
        - Do not miss any line and strive for full coverage of translation. 
        The output format must follow the following pattern:
        - ensure its ONLY a valid JSON response. No other content should be there. 
        - JSON must include 2 fields - {{"answer": {{"<language_code>": "<translated_answer>"}}, "status": "pass or fail"}}. The answer field must be a dictionary of the language code as found in the values of <LANGUAGE_CODE_MAP>, and its corresponding translated text in that language. If translations to all languages specified in the <LANGUAGE_CODE_MAP> was completed, only then "status" field is to be marked as "pass" otherwise it should be marked as a "fail".
        - Do not allow translations for more than 10 languages at a time in one request.  
        - Do not return with any other response format other than the json in case of errors and add a status field as "fail". Optionally include an "error_msg" string field if status is fail indicating reason for failure. 
        """


def get_translation_prompt(text, lang):
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
        {LANG_CODE_MAP}
        </LANGUAGE_CODE_MAP
        """


PLATFORMS = {
    "audio": ["youtube", "soundcloud", "spotify", "apple_podcasts", "google_podcasts"],
    "video": ["youtube", "vimeo"]
}


class ContentConfig:
    def __init__(self, name, source_path, source_type, source_lang, background_music, translations,
                 publishing_platforms,
                 generate_ai_description, generate_milestones, split_into_parts, from_chunk):
        self.name = name
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
        return cls(
            name=data['name'],
            source_path=data['source']['path'],
            source_type=data['content_type'],
            source_lang=data['source']['language'],
            background_music=data['background_music']['path'],
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
