import unittest

from utils.validators import extract_video_id, validate_youtube_url

VIDEO_ID = "dQw4w9WgXcQ"


class TestYouTubeUrlValidation(unittest.TestCase):
    def test_watch_url(self):  # TC002
        self.assertEqual(extract_video_id(f"https://www.youtube.com/watch?v={VIDEO_ID}"), VIDEO_ID)

    def test_short_url(self):  # TC003
        self.assertEqual(extract_video_id(f"https://youtu.be/{VIDEO_ID}"), VIDEO_ID)

    def test_shorts_url(self):  # TC004
        self.assertEqual(extract_video_id(f"https://www.youtube.com/shorts/{VIDEO_ID}"), VIDEO_ID)

    def test_embed_url(self):  # TC005
        self.assertEqual(extract_video_id(f"https://www.youtube.com/embed/{VIDEO_ID}"), VIDEO_ID)

    def test_url_with_extra_params(self):
        url = f"https://www.youtube.com/watch?v={VIDEO_ID}&t=42s"
        self.assertEqual(extract_video_id(url), VIDEO_ID)

    def test_other_website(self):  # TC006
        self.assertFalse(validate_youtube_url(f"https://www.facebook.com/watch?v={VIDEO_ID}"))

    def test_empty_url(self):  # TC007
        self.assertFalse(validate_youtube_url(""))

    def test_invalid_video_id(self):  # TC008
        self.assertFalse(validate_youtube_url("https://www.youtube.com/watch?v=abc"))


if __name__ == "__main__":
    unittest.main()
