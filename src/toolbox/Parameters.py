import json
import logging
import os.path

from toolbox.Singleton import SingletonMeta


class Params(metaclass=SingletonMeta):
    params_dict = {}

    @staticmethod
    def save_params_to_json(save_params_dict: dict, filename: str) -> None:
        """
        Save parameters from a dictionary to a JSON file.
        :param save_params_dict: Dictionary containing parameters to save
        :param filename: Path to save the JSON file
        """
        with open(filename, 'w') as f:
            json.dump(save_params_dict, f, indent=4)
        logging.info(f"Parameters successfully saved to {filename}")

    def load_params_from_json(self, filename: str) -> None:
        """
        Load parameters from a JSON file back into a dictionary.
        :param filename: Path to the JSON file to load
        :return: Dictionary containing the loaded parameters
        """
        if not os.path.exists(filename):
            self.params_dict = {}
            return
        with open(filename, 'r') as f:
            self.params_dict = json.load(f)
        logging.info(f"Parameters successfully loaded from {filename}")

    def get_max_workers(self) -> int:
        """
        return number max of workers, default: 5
        """
        if "max_workers" in self.params_dict:
            return int(self.params_dict["max_workers"])
        return int(5)

    def get_vcodec(self) -> str:
        """
        return default video codec, default: hevc_nvenc
        """
        if "vcodec" in self.params_dict:
            return self.params_dict["vcodec"]
        return "hevc_nvenc"
