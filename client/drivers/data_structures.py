"""
Data structures for use on the RPi Client.

Author:
    Gabriel Field (47484306), Mitchell Clark
"""

import logging
import time
from datetime import datetime
from math import pi, sin
from queue import Queue
from typing import List

from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
from PiicoDev_SSD1306 import *
from PiicoDev_Switch import PiicoDev_Switch

#: Sentinel value for an invalid user.
EMPTY_USER_ID = -1

LEFT_BUTTON = 0
RIGHT_BUTTON = 1
DOUBLE_RIGHT_BUTTON = 2

logger = logging.getLogger(__name__)


class ControlledData:
    """
    Data for passing around in client/drivers/main.run_user_session().

    There should only ever be one object of this class at a time.

    Attributes:
        _failed: True if this data is incomplete.
        _user_id: ID of current user.
        _posture_data: Data updated through ML models, used for feedback
        _last_snapshot_time: Time of the last successful pull of posture data from the SQLite database
        _last_cushion_time: Time of the last successful cushion feedback event.
        _last_plant_time: Time of the last successful plant feedback event.

    Class invariant:
        self._failed ==> (all other variables are default values)
    """

    _failed: bool
    _user_id: int
    _posture_data: Queue[float]
    _last_snapshot_time: datetime
    _last_cushion_time: datetime
    _last_plant_time: datetime

    # SECTION: Constructors

    def __init__(self):
        """
        DO NOT USE THIS CONSTRUCTOR! Call ControlledData.make_empty() or ControlledData.make_failed() instead.
        """
        self._failed = True
        self._user_id = EMPTY_USER_ID
        self._posture_data = Queue()
        self._last_snapshot_time = datetime.now()
        self._last_cushion_time = datetime.now()
        self._last_plant_time = datetime.now()
        self._DEBUG_current_graph_list_index = 0
        self._DEBUG_current_graph_function = lambda x: 30 * (
            1 + sin(2 * pi * x / WIDTH)
        )

    @classmethod
    def make_empty(cls, user_id: int) -> "ControlledData":
        """
        Construct a non-failed object of this class, with a provided user ID and empty posture data.

        Returns:
            An object of this class that is not failed, with legal user ID and empty posture data.
        """
        return_me = ControlledData()
        return_me._failed = False
        return_me._user_id = user_id
        return_me._posture_data = Queue()
        return_me._last_snapshot_time = datetime.now()
        return_me._last_cushion_time = datetime.now()
        return_me._last_plant_time = datetime.now()
        logger.debug(
            "<!> Made a new empty ControlledData() with user_id %d", return_me._user_id
        )
        return return_me

    @classmethod
    def make_failed(cls) -> "ControlledData":
        """
        Construct and return a failed object of this class.
        """
        return_me = ControlledData()
        return_me._failed = True
        return_me._user_id = EMPTY_USER_ID
        return_me._posture_data = Queue()
        return_me._last_snapshot_time = datetime.now()
        return_me._last_cushion_time = datetime.now()
        return_me._last_plant_time = datetime.now()
        return return_me

    # SECTION: Getters/Setters

    def is_failed(self) -> bool:
        """
        Returns True iff this ControlledData is failed.
        """
        return self._failed

    def get_user_id(self) -> int:
        """
        Returns the user id of this ControlledData.
        """
        return self._user_id

    def get_posture_data(self) -> Queue[float]:
        """
        Returns the posture data stored in this ControlledData.
        """
        return self._posture_data

    def get_last_snapshot_time(self) -> datetime:
        """
        Returns the last time that the internal posture data was updated.
        """
        return self._last_snapshot_time

    def set_last_snapshot_time(self, time: datetime) -> None:
        """
        Args:
            time: the last time that the internal posture data was updated.
        """
        self._last_snapshot_time = time

    def get_last_cushion_time(self) -> datetime:
        """
        Returns the last time that the user was provided cushion feedback.
        """
        return self._last_cushion_time

    def set_last_cushion_time(self, time: datetime) -> None:
        """
        Args:
            time: the last time that the user was provided cushion feedback.
        """
        self._last_cushion_time = time

    def get_last_plant_time(self) -> datetime:
        """
        Returns the last time that the user was provided plant feedback.
        """
        return self._last_plant_time

    def set_last_plant_time(self, time: datetime) -> None:
        """
        Args:
            time: the last time that the user was provided plant feedback.
        """
        self._last_plant_time = time

    def accept_new_posture_data(self, posture_data: List[float]) -> None:
        """
        Update the internal store of posture data for the OLED display.

        Args:
            posture_data: new posture data to accept and merge with the current state of this object.

        """
        logger.debug("<!> accept_new_posture_data()")
        for datum in posture_data:
            self._posture_data.put_nowait(datum)


class HardwareComponents:
    """
    Hardware components packaged together into a class.

    Attributes:
        button0: A button with address switches set to [0, 0, 0, 0]
        button1: A button with address switches set to [0, 0, 0, 1]
        display: OLED SSD1306 Display with default address
        posture_graph: Graph object for rendering on self.display. NOT INITIALISED by
                       default; i.e. None until initialised. Should get initialised ONCE
                       THE USER IS LOGGED IN because the graph will look different for
                       each user.
        posture_graph_from: y-coordinate from which the posture graph begins, or `None`
                            if no posture graph is active.

        plant_mover: Continuous rotation servo driving the I. Jensen Plant Mover 10000.
                     Its `midpoint_us` is `1600`.
        plant_height: Height of the plant, With a maximum given by
                      (_PLANT_SHAFT_TURNS - _PLANT_SHAFT_SAFETY_BUFFER_TURNS - 1).
        _PLANT_SHAFT_TURNS: Maximum number of turns that can be made on the plant-moving
                            shaft before damaging the product.
        _PLANT_SHAFT_SAFETY_BUFFER_TURNS: Number of turns on the plant-moving shaft to
                                          leave as a buffer, to ensure we don't damage
                                          the product.
        _PLANT_GEAR_RATIO: Gear ratio between the plant-moving shaft and the continuous
                           servo controlled by this HardwareComponents. To obtain `x`
                           full rotations of the plant-moving shaft, make
                           `x * _PLANT_GEAR_RATIO` full rotations of the `plant_mover`.
        _PLANT_MOVER_PERIOD: Period (in milliseconds) for one full turn of the
                             continuous rotation servo. To make a full turn of the
                             continuous rotation servo, set its `.speed` to
                             `_FULL_SPEED_UPWARDS` or `_FULL_SPEED_DOWNWARDS` and wait
                             `_PLANT_MOVER_PERIOD * _PLANT_GEAR_RATIO` milliseconds.
                            WARNING: This value may be different once we put some load on the plant mover!
                            TODO: Check this value against what happens when we put the plant mover on it.
                            NOTE: This is NON-LINEAR with the `.speed` attribute, for whatever reason.
        _BASE_FULL_SPEED: Top speed for the `PiicoDev_Servo` in our application.
        _FULL_SPEED_UPWARDS: Value for the `PiicoDev_Servo`'s `.speed` attribute when
                             moving the plant up.
                             TODO: Check this value indeed drives the plant UP, not down.
                             NOTE: This is asymmetric with `_FULL_SPEED_DOWNWARDS`. I don't know why.
        _FULL_SPEED_DOWNWARDS: Value for the `PiicoDev_Servo`'s `.speed` attribute when
                               moving the plant down.
                               TODO: Check this value indeed drives the plant DOWN, not UP.
    """

    button0: PiicoDev_Switch
    button1: PiicoDev_Switch
    display: PiicoDev_SSD1306
    posture_graph: PiicoDev_SSD1306.graph2D | None
    posture_graph_from: int | None

    plant_mover: PiicoDev_Servo
    plant_height: int
    _PLANT_SHAFT_TURNS: int = 13
    _PLANT_SHAFT_SAFETY_BUFFER_TURNS: int = 3
    _PLANT_GEAR_RATIO: float = 2
    _PLANT_MOVER_PERIOD: float = 1000 * 60 / 55
    _BASE_FULL_SPEED = 0.1
    _FULL_SPEED_UPWARDS = _BASE_FULL_SPEED * (4 / 7) * (17 / 20) * 2
    _FULL_SPEED_DOWNWARDS = (-1) * _BASE_FULL_SPEED * (6 / 10) * 2

    # SECTION: Constructors

    @classmethod
    def make_fresh(cls):
        """
        Create a new instance of HardwareComponents, set up according to the hardware that we expect
        to be plugged in.
        """
        DOUBLE_PRESS_DURATION = 400  # Milliseconds
        return HardwareComponents(
            PiicoDev_Switch(
                id=[0, 0, 0, 0], double_press_duration=DOUBLE_PRESS_DURATION
            ),  # WARNING: 2024-09-01 17:12 Gabe: I think this produces an "I2C is not enabled" warning. No idea why.
            PiicoDev_Switch(
                id=[0, 0, 0, 1], double_press_duration=DOUBLE_PRESS_DURATION
            ),  # WARNING: 2024-09-01 17:12 Gabe: I think this produces an "I2C is not enabled" warning. No idea why.
            create_PiicoDev_SSD1306(),  # This is the constructor; ignore the "is not defined" error message.
            PiicoDev_Servo(PiicoDev_Servo_Driver(), 1, midpoint_us=1600, range_us=1800),
        )

    def __init__(self, button0, button1, display, plant_mover):
        self.button0: PiicoDev_Switch = button0
        self.button1: PiicoDev_Switch = button1
        self.display: PiicoDev_SSD1306 = display
        self.posture_graph: PiicoDev_SSD1306.graph2D | None = None
        self.posture_graph_from: int | None = None
        self.plant_mover: PiicoDev_Servo = plant_mover
        self.plant_height: int = 0
        self.plant_mover.speed = 0  # Stop the plant mover from spinning.
        self.unwind_plant()

    # SECTION: Setters

    def get_control_messages(self, user_id: int) -> List[str]:
        """
        Get messages to display during usual application loop.
        TODO: Finalise these!

        Args:
            user_id: ID of the currently logged-in user.

        Returns:
            The messages to display to the user during the main application loop.
        """
        return ["Left: logout", "ID: " + str(user_id)]

    def initialise_posture_graph(self, user_id: int) -> None:
        """
        Initialise self.posture_graph according to the provided user_id.

        Args:
            user_id: ID of the currently logged-in user.
        """
        CONTROL_MESSAGES = self.get_control_messages(user_id)
        GRAPH_MIN_VALUE = 0
        GRAPH_MAX_VALUE = 1
        LINE_HEIGHT = 15  # pixels
        LINE_WIDTH = 16  # characters

        # The posture graph will occupy space from the bottom (y = HEIGHT - 1) up to initialisation_y_value.
        flatten = lambda xss: [x for xs in xss for x in xs]
        it = flatten(
            map(
                (
                    lambda me: [
                        me[i : i + LINE_WIDTH]
                        for i in range(0, len(CONTROL_MESSAGES), LINE_WIDTH)
                    ]
                ),
                CONTROL_MESSAGES,
            )
        )
        initialisation_y_value = len(it) * LINE_HEIGHT
        self.posture_graph_from = initialisation_y_value
        self.posture_graph = self.display.graph2D(
            originX=0,
            originY=HEIGHT - 1,
            width=WIDTH,
            height=HEIGHT - initialisation_y_value,
            minValue=GRAPH_MIN_VALUE,
            maxValue=GRAPH_MAX_VALUE,
            c=1,
            bars=False,
        )

    # SECTION: Using peripherals

    def unwind_plant(self) -> None:
        """
        Unwind the plant to its maximum height, by making 15 full turns (we have 13 turns total).
        """
        self.plant_mover.speed = self._FULL_SPEED_UPWARDS
        time.sleep(15 * self._PLANT_MOVER_PERIOD * self._PLANT_GEAR_RATIO / 1000)
        self.plant_height = (
            self._PLANT_SHAFT_TURNS - self._PLANT_SHAFT_SAFETY_BUFFER_TURNS
        )
        self.plant_mover.speed = 0

    def wind_plant_safe(self) -> None:
        """
        Wind the plant down to its minimum (safe) height.
        Will also reset the `plant_height` to `0`.
        """
        self.set_plant_height(0)

    def set_plant_height(self, new_height: int) -> None:
        """
        Move the plant to a desired height.

        Args:
            new_height: height to which to drive the I. Jensen Plant Mover 10000
        """
        self.plant_mover.speed = 0
        logger.debug(f"<!> set_plant_height: {self.plant_height=}, {new_height=}")
        distance = new_height - self.plant_height
        distance = distance if distance > 0 else (-1) * distance
        if new_height == self.plant_height:
            self.plant_mover.speed = 0
            return
        if (
            new_height
            > self._PLANT_SHAFT_TURNS - self._PLANT_SHAFT_SAFETY_BUFFER_TURNS - 1
        ):
            logger.debug(
                "<!> Plant mover not schmovin': can't get that high mate, that's just unsafe"
            )
            self.plant_mover.speed = 0
            return
        if new_height < 0:
            logger.debug(
                "<!> Plant mover not schmovin': can't get that low mate, that's just dirty"
            )
            self.plant_mover.speed = 0
            return
        if new_height > self.plant_height:
            self.plant_mover.speed = self._FULL_SPEED_UPWARDS
            time.sleep(
                distance * self._PLANT_MOVER_PERIOD * self._PLANT_GEAR_RATIO / 1000
            )
            self.plant_mover.speed = 0
            self.plant_height = new_height
            return
        self.plant_mover.speed = self._FULL_SPEED_DOWNWARDS
        time.sleep(distance * self._PLANT_MOVER_PERIOD * self._PLANT_GEAR_RATIO / 1000)
        self.plant_mover.speed = 0
        self.plant_height = new_height
        return

    def oled_display_text(self, text: str, x: int, y: int, colour: int = 1) -> int:
        """
        Display text on the oled display, wrapping lines if necessary.
        NOTE: Does not blank display. Call `.display.fill(0)` if needed.
        NOTE: Does not render. Call `.display.show()` if needed.

        Args:
            text: string to write to the OLED display.
            x: horizontal coordinate from left side of screen.
            y: vertical coordinate from top side of screen.
            colour: 0 (black), 1 (white), defaults to 1.

        Returns:
            The y-value at which any subsequent lines should start printing from.
        """
        LINE_HEIGHT = 15  # pixels
        LINE_WIDTH = 16  # characters
        chunks = [text[i : i + LINE_WIDTH] for i in range(0, len(text), LINE_WIDTH)]
        for index, chunk in enumerate(chunks):
            self.display.text(chunk, x, y + index * LINE_HEIGHT, colour)
        return y + len(chunks) * LINE_HEIGHT

    def oled_display_texts(self, texts: List[str], x: int, y: int, colour: int) -> int:
        """
        Display many lines of text on the oled display, wrapping lines if necessary.
        NOTE: Does not blank display. Call `.display.fill(0)` if needed.
        NOTE: Does not render. Call `.display.show()` if needed.

        Args:
            texts: strings to write to the OLED display. Each string begins on a new line.
            x: horizontal coordinate from left side of screen.
            y: vertical coordinate from top side of screen.
            colour: 0 (black), 1 (white)

        Returns:
            The y-value at which any subsequent lines should start printing from.
        """
        display_height_offset = 0
        for text in texts:
            display_height_offset = self.oled_display_text(
                text, x, y + display_height_offset, colour
            )
        return display_height_offset

    def send_message(self, messages: List[str], message_time: int = 1) -> None:
        """Clear the screen and display message

        Args:
            message: Message to send to the user
            message_time: Time (seconds) to sleep for after displaying message.
        """
        self.display.fill(0)
        display_height_offset = 0
        for text in messages:
            display_height_offset = self.oled_display_text(
                text, 0, 0 + display_height_offset, 1
            )
        self.display.show()
        time.sleep(message_time)

    def wait_for_button_press(self) -> int:
        """Waits for a button to be pressed and then returns the button number.

        Returns:
            The number of the button pressed.
        """
        self._clear_buttons()
        while True:
            pressed_button = -1

            # Checking double press first as double press implies single press
            if self.button1.was_double_pressed:
                pressed_button = DOUBLE_RIGHT_BUTTON
            elif self.button0.was_pressed:
                pressed_button = LEFT_BUTTON
            elif self.button1.was_pressed:
                pressed_button = RIGHT_BUTTON

            if pressed_button != -1:
                self._clear_buttons()
                return pressed_button

            time.sleep(0.5)

    def _clear_buttons(self) -> None:
        """Clear pressed status from all buttons."""
        self.button0.was_pressed
        self.button1.was_pressed
        self.button0.was_double_pressed
        self.button1.was_double_pressed
