import numpy as np
import face_recognition

from data.routines import register_face_embeddings, iter_face_embeddings

MODEL_NAME = "small"
TOO_MANY_FACES = -2
NO_MATCH = -1
OK = 0


def get_face_match(login_face: np.ndarray) -> int:
    """
    Matches the given face to one of the user ids in the database.

    Args:
        login_face: Image of user's face as an array

    Returns:
        Matching user id, -1 if no users matched, -2 if too many faces
    """
    login_embeddings = face_recognition.face_encodings(login_face, model=MODEL_NAME)

    # Should only detect one face
    if len(login_embeddings) != 1:
        return TOO_MANY_FACES
    login_embedding = login_embeddings[0]

    for user_id, user_embeddings in iter_face_embeddings():
        matches = face_recognition.compare_faces(user_embeddings, login_embedding)

        if any(matches):
            return user_id

    return NO_MATCH


def register_faces(user_id: int, faces: list[np.ndarray]) -> int:
    """Compute and store face embeddings in the database.

    Args:
        user_id: Id of the user who belongs to the faces
        faces: List of face images in the shape HxWxC where (C)hannels are in RGB

    Returns:
        Status, -2 if too many faces in an image, 0 if registration was sucessful.
    """
    face_embeddings = []
    for face in faces:
        all_faces_embed = face_recognition.face_encodings(face, model=MODEL_NAME)

        # Should only detect one face
        if len(all_faces_embed) != 1:
            return TOO_MANY_FACES

        face_embedding = all_faces_embed[0]
        face_embeddings.append(face_embedding)

    register_face_embeddings(user_id, face_embeddings)

    return OK
