import re
import numpy as np
from unicodedata import normalize

# Adapted from https://github.com/supertone-inc/supertonic/blob/main/py/helper.py
# Modified to work with Supertonic 1.0.0 call signature

class EnhancedKoreanProcessor:
    def __init__(self, indexer):
        self.indexer = indexer # List or Dict from the loaded model
        
    def validate_text(self, text):
        # We perform our own cleaning, so we tell the engine it's always valid
        return True, []

    def _preprocess_text(self, text: str, lang: str = "ko") -> str:
        # Normalize
        text = normalize("NFKD", text)

        # Remove emojis (wide Unicode range)
        emoji_pattern = re.compile(
            "[\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f700-\U0001f77f"
            "\U0001f780-\U0001f7ff"
            "\U0001f800-\U0001f8ff"
            "\U0001f900-\U0001f9ff"
            "\U0001fa00-\U0001fa6f"
            "\U0001fa70-\U0001faff"
            "\u2600-\u26ff"
            "\u2700-\u27bf"
            "\U0001f1e6-\U0001f1ff]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub("", text)

        # Replace various dashes and symbols
        replacements = {
            "–": "-", "‑": "-", "—": "-", "_": " ",
            "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
            "´": "'", "`": "'",
            "[": " ", "]": " ", "|": " ", "/": " ", "#": " ",
            "→": " ", "←": " ",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

        # Remove special symbols
        text = re.sub(r"[♥☆♡©\\]", "", text)

        # Replace known expressions (English focused, but safe to keep)
        expr_replacements = {
            "@": " at ",
            "e.g.,": "for example, ",
            "i.e.,": "that is, ",
        }
        for k, v in expr_replacements.items():
            text = text.replace(k, v)

        # Fix spacing around punctuation
        text = re.sub(r" ,", ",", text)
        text = re.sub(r" \.", ".", text)
        text = re.sub(r" !", "!", text)
        text = re.sub(r" \?", "?", text)
        text = re.sub(r" ;", ";", text)
        text = re.sub(r" :", ":", text)
        text = re.sub(r" '", "'", text)

        # Remove duplicate quotes
        while '""' in text: text = text.replace('""', '"')
        while "''" in text: text = text.replace("''", "'")
        while "``" in text: text = text.replace("``", "`")

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()

        # If text doesn't end with punctuation, add a period
        if text and not re.search(r"[.!?;:,'\"')\]}…。」』】〉》›»]$", text):
            text += "."

        # Wrap in language tag
        text = f"<{lang}>" + text + f"</{lang}>"
        return text

    def _get_text_mask(self, text_ids_lengths: np.ndarray) -> np.ndarray:
        # Re-implementation of length_to_mask logic
        max_len = text_ids_lengths.max()
        mask = np.arange(max_len)[None, :] < text_ids_lengths[:, None]
        mask = mask.astype(np.float32)
        return mask[:, None, :] # [B, 1, T]

    # COMPATIBILITY: Method signature MUST match what Supertonic 1.0.0 expects
    def __call__(self, text_list: list[str]):
        # Hardcode lang to 'ko' for this application
        lang = 'ko'
        
        processed_list = []
        for t in text_list:
            processed_list.append(self._preprocess_text(t, lang))
            
        text_ids_lengths = np.array([len(text) for text in processed_list], dtype=np.int64)
        max_len = text_ids_lengths.max() if len(text_ids_lengths) > 0 else 0
        
        text_ids = np.zeros((len(processed_list), max_len), dtype=np.int64)
        
        for i, text in enumerate(processed_list):
            unicode_vals = [ord(char) for char in text]
            # Map values using the indexer
            mapped_ids = []
            for val in unicode_vals:
                if val < len(self.indexer):
                    mapped_ids.append(self.indexer[val])
                else:
                    mapped_ids.append(0) # Unknown token
            
            text_ids[i, :len(mapped_ids)] = np.array(mapped_ids, dtype=np.int64)
            
        text_mask = self._get_text_mask(text_ids_lengths)
        return text_ids, text_mask
