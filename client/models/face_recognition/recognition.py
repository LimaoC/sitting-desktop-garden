from enum import Enum

import numpy as np
import face_recognition

from data.routines import register_face_embeddings, iter_face_embeddings

MODEL_NAME = "small"
TOLERANCE = 0.3


class Status(Enum):
    ALREADY_REGISTERED = -4
    NO_FACES = -3
    TOO_MANY_FACES = -2
    NO_MATCH = -1
    OK = 0


def get_face_match(login_face: np.ndarray) -> int:
    """
    Matches the given face to one of the user ids in the database.

    Args:
        login_face: Image of user's face as an array

    Returns:
        Matching user id, or one of Status values.
    """
    login_embeddings = face_recognition.face_encodings(login_face, model=MODEL_NAME)

    # Should only detect exactly one face
    if len(login_embeddings) == 0:
        return Status.NO_FACES.value
    if len(login_embeddings) > 1:
        return Status.TOO_MANY_FACES.value

    login_embedding = login_embeddings[0]

    for user_id, user_embeddings in iter_face_embeddings():
        matches = face_recognition.compare_faces(
            user_embeddings, login_embedding, tolerance=TOLERANCE
        )

        if any(matches):
            return user_id

    return Status.NO_MATCH.value


def register_faces(user_id: int, faces: list[np.ndarray]) -> int:
    """Compute and store face embeddings in the database.

    Args:
        user_id: Id of the user who belongs to the faces
        faces: List of face images in the shape HxWxC where (C)hannels are in RGB

    Returns:
        Registration status
    """
    face_embeddings = []
    for face in faces:
        all_faces_embed = face_recognition.face_encodings(face, model=MODEL_NAME)

        # Should only detect exactly one face
        if len(all_faces_embed) == 0:
            return Status.NO_FACES.value
        if len(all_faces_embed) > 1:
            return Status.TOO_MANY_FACES.value

        face_embedding = all_faces_embed[0]
        face_embeddings.append(face_embedding)

    # Ensure that all images contain the same face
    matches = face_recognition.compare_faces(
        face_embeddings[1:], face_embeddings[0], tolerance=TOLERANCE
    )
    if not all(matches):
        return Status.TOO_MANY_FACES.value

    # Ensure user is not already registered
    for _, other_user_embeddings in iter_face_embeddings():
        for embedding in face_embeddings:
            matches = face_recognition.compare_faces(
                other_user_embeddings, embedding, tolerance=TOLERANCE
            )

            if any(matches):
                return Status.ALREADY_REGISTERED.value

    register_face_embeddings(user_id, face_embeddings)

    return Status.OK.value
