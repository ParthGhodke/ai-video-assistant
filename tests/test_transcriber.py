import os
import unittest
from unittest.mock import patch

from core.transcriber import resolve_whisper_model


class WhisperModelSelectionTests(unittest.TestCase):
    def test_defaults_to_tiny_en_when_env_missing(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WHISPER_MODEL", None)
            self.assertEqual(resolve_whisper_model(), "tiny.en")

    def test_honors_explicit_model_env(self):
        with patch.dict(os.environ, {"WHISPER_MODEL": "small"}, clear=False):
            self.assertEqual(resolve_whisper_model(), "small")


if __name__ == "__main__":
    unittest.main()
