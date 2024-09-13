import numpy as np


def get_user_from_face(face: np.ndarray) -> int:
    """
    Args:
        face: Face image to identify user from in format HxWxC where channels are in RGB order.

    Returns:
        The id of the matched user. Returns -1 if no user matched.
    """
    raise NotImplementedError()
