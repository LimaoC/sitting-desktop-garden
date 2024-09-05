import time
from pprint import pprint
from datetime import datetime
from data.routines import (
    init_database,
    get_schema_info,
    create_user,
    save_posture,
    get_users,
    get_postures,
    get_user_postures,
    Posture,
)

print("Initialising database")
init_database()

print("Schema info")
pprint(get_schema_info())

print("Creating user")
create_user()

print("Getting 10 users")
pprint(get_users(num=10))

print("Adding posture for user 1")
time1 = datetime.now()
time.sleep(1)
time2 = datetime.now()
posture = Posture(None, 1, 0.8, 1.0, time1, time2)
save_posture(posture)

print("Getting 10 postures")
pprint(get_postures(num=10))

print("Getting postures for user 1")
pprint(get_user_postures(1))
