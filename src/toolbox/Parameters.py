import json
import logging
import os.path

from Singleton import SingletonMeta

class Params(metaclass=SingletonMeta):
    params_dict = {}

    def __init__(self, load_path:str|None) -> None:
        if load_path is None: return
        if os.path.exists(load_path):
            self.load_params_from_json(load_path)
        else:
            logging.error(f"File not found: {load_path}")


    def save_params_to_json(self, params_dict:dict, filename:str) -> None:
        """
        Save parameters from a dictionary to a JSON file.
        :param params_dict: Dictionary containing parameters to save
        :param filename: Path to save the JSON file
        """
        with open(filename, 'w') as f:
            json.dump(params_dict, f, indent=4)
        logging.info(f"Parameters successfully saved to {filename}")
    
    
    def load_params_from_json(self, filename: str) -> None:
        """
        Load parameters from a JSON file back into a dictionary.
        :param filename: Path to the JSON file to load
        :return: Dictionary containing the loaded parameters
        """
        with open(filename, 'r') as f:
            self.params_dict = json.load(f)
        logging.info(f"Parameters successfully loaded from {filename}")


if __name__ == "__main__":
    # The client code.

    s1 = Params(None)
    s2 = Params("")
    s2.max_workers = 3

    if id(s1) == id(s2):
        print(s1.max_workers, s2.max_workers)