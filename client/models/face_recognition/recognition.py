from importlib import resources

import numpy as np
from data.routines import FACES_FOLDER, register_face_embeddings, iter_face_embeddings
from deepface import DeepFace
import face_recognition

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
    # with resources.as_file(FACES_FOLDER) as faces_folder:
    #     try:
    #         dfs = DeepFace.find(login_face, str(faces_folder), model_name=MODEL_NAME)
    #     except ValueError:
    #         return -1
    #     df = dfs[0]
    #     user_id = int(_path_to_user_id(df.iloc[0]["identity"]))
    #     return user_id

    login_embeddings = face_recognition.face_encodings(login_face, model="small")

    # Should only detect one face
    if len(login_embeddings) != 1:
        return -1
    login_embedding = login_embeddings[0]

    for user_id, user_embeddings in iter_face_embeddings():
        matches = face_recognition.compare_faces(user_embeddings, login_embedding)

        if any(matches):
            return user_id

    return -1


def register_faces(user_id: int, faces: list[np.ndarray]) -> int:
    face_embeddings = []
    for face in faces:
        all_faces_embed = face_recognition.face_encodings(face, model="small")

        # Should only detect one face
        if len(all_faces_embed) != 1:
            return -1

        face_embedding = all_faces_embed[0]
        face_embeddings.append(face_embedding)

    register_face_embeddings(user_id, face_embeddings)

    return 0
