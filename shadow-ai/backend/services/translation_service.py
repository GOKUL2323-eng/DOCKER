from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import logging

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class TranslationService:
    THANGLISH_KEYWORDS = {
        'enna', 'summa', 'panra', 'panren', 'epdi', 'eppadi', 'irukinga', 'iruka', 
        'saptingala', 'solla', 'sollunga', 'theriyum', 'puriyala', 'yaaru', 'enga', 
        'enge', 'yen', 'nalla', 'aama', 'illa', 'vanakkam', 'machan', 'thala', 'bro'
    }

    @classmethod
    def is_thanglish(cls, text: str) -> bool:
        """Check if text contains common Thanglish keywords."""
        if not text:
            return False
        words = set(text.lower().split())
        return bool(words.intersection(cls.THANGLISH_KEYWORDS))

    @classmethod
    def detect_language(cls, text: str) -> str:
        """Detect the language of the input text."""
        try:
            if not text or len(text.strip()) < 2:
                return 'en'
            if cls.is_thanglish(text):
                return 'ta-Latn'
            return detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'

    @staticmethod
    def translate(text: str, target_lang: str = 'en', source_lang: str = 'auto') -> str:
        """Translate text to the target language with robust encoding handling."""
        try:
            if not text or text.strip() == "":
                return text
            
            # Clean input text from any surrogates that might cause encoding errors
            clean_text = text.encode('utf-8', 'ignore').decode('utf-8')
            
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(clean_text)
            return translated
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Fallback: if it's an encoding issue, try to return a cleaned version of the original
            return text.encode('utf-8', 'ignore').decode('utf-8')

    @classmethod
    def to_english(cls, text: str) -> tuple[str, str]:
        """Detect language and translate to English. Returns (translated_text, detected_lang)."""
        detected_lang = cls.detect_language(text)
        if detected_lang == 'en':
            return text, 'en'
        
        translated = cls.translate(text, target_lang='en', source_lang=detected_lang)
        return translated, detected_lang

    @classmethod
    def from_english(cls, text: str, target_lang: str) -> str:
        """Translate from English back to the target language."""
        if target_lang == 'en':
            return text
        return cls.translate(text, target_lang=target_lang, source_lang='en')
