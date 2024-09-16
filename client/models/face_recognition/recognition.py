from importlib import resources

import numpy as np
from data.routines import FACES_FOLDER
from deepface import DeepFace

MODEL_NAME = "GhostFaceNet"


def _path_to_user_id(path: str) -> str:
    return path.split("/")[-2]


def get_face_match(login_face: np.ndarray) -> int:
    """
    Matches the given face to one of the user ids in the database.

    Args:
        login_face: Image of user's face as an array

    Returns:
        Matching user id, or -1 if no users matched
    """
    with resources.as_file(FACES_FOLDER) as faces_folder:
        try:
            dfs = DeepFace.find(login_face, str(faces_folder), model_name=MODEL_NAME)
        except ValueError:
            return -1
        df = dfs[0]
        user_id = _path_to_user_id(df.iloc[0]["identity"])
        return user_id
