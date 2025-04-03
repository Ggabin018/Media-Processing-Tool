import os
import unittest

from file_manipulation.video_modif import get_video_duration, get_resolution, get_video_bitrate, get_original_codecs


class TestVideoProcessing(unittest.TestCase):

    def test_file_exists(self):
        v_path = "videos/test.mp4"
        self.assertTrue(os.path.exists(v_path))

    def test_file_not_found(self):
        v_path = "nonexistent.mp4"
        self.assertFalse(os.path.exists(v_path))

    def test_get_video_duration(self):
        v_path = "videos/test.mp4"
        expected_duration = 187.0  # Expected duration in seconds
        self.assertEqual(get_video_duration(v_path), expected_duration)

    def test_get_resolution(self):
        v_path = "videos/test.mp4"
        expected_resolution = (1920, 1080)
        self.assertEqual(get_resolution(v_path), expected_resolution)

    def test_get_video_bitrate(self):
        v_path = "videos/test.mp4"
        expected_bitrate = 1423.64  # Expected bitrate in kbps
        self.assertEqual(get_video_bitrate(v_path), expected_bitrate)

    def test_get_original_codecs(self):
        v_path = "videos/test.mp4"
        expected_codecs = ('hevc', 'aac')
        self.assertEqual(get_original_codecs(v_path), expected_codecs)


if __name__ == "__main__":
    unittest.main()
