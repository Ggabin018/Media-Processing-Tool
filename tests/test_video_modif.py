import os
import unittest

from back_end.video_manip import get_video_duration, get_resolution, get_video_bitrate, get_original_codecs, \
    is_video


class TestVideoProcessing(unittest.TestCase):

    # check if test file exists
    def test_file_exists(self):
        v_path = "videos/test.mp4"
        self.assertTrue(os.path.exists(v_path))

    def test_get_video_duration(self):
        v_path = "videos/test.mp4"
        expected_duration = 187.0
        self.assertEqual(get_video_duration(v_path), expected_duration)

    def test_get_resolution(self):
        v_path = "videos/test.mp4"
        expected_resolution = (1920, 1080)
        self.assertEqual(get_resolution(v_path), expected_resolution)

    def test_get_video_bitrate(self):
        v_path = "videos/test.mp4"
        expected_bitrate = 1423.64
        self.assertEqual(get_video_bitrate(v_path), expected_bitrate)

    def test_get_original_codecs(self):
        v_path = "videos/test.mp4"
        expected_codecs = ('hevc', 'aac')
        self.assertEqual(get_original_codecs(v_path), expected_codecs)

    def test_not_a_video(self):
        v_path = "videos/not_a_video.wav"
        self.assertFalse(is_video(v_path))


if __name__ == "__main__":
    unittest.main()
