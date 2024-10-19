import time
import logging
import datetime
import pprint

from data.routines import (
    destroy_database,
    init_database,
    create_user,
    save_posture,
    Posture,
    get_users,
    get_postures,
    clear_database,
)

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Destroying database")
    destroy_database()

    logger.info("Initialising database")
    start_time = time.time()
    init_database()
    total_time = time.time() - start_time
    logger.info("Done init database in %f seconds", total_time)

    logger.info("Filling with some data")

    for _ in range(10):
        _fill_database()

    logger.info(
        "Example data\n%s\n%s",
        pprint.pformat(get_users(), width=50),
        pprint.pformat(get_postures(), width=50),
    )

    logger.info("Reseting data by dropping rows")
    start_time = time.time()
    clear_database()
    total_time = time.time() - start_time
    logger.info("Done clearing data in %f", total_time)

    logger.info(
        "Example data\n%s\n%s",
        pprint.pformat(get_users(), width=50),
        pprint.pformat(get_postures(), width=50),
    )


def _fill_database() -> None:
    create_user()
    example_id = create_user()
    create_user()

    example_posture = Posture(
        None, example_id, 0.8, 0.8, datetime.datetime.now(), datetime.datetime.now()
    )
    save_posture(example_posture)


if __name__ == "__main__":
    main()
