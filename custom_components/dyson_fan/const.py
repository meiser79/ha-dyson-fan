"""Constants for the Dyson Fan integration."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "dyson_fan"
DEFAULT_NAME: Final = "Dyson Fan"

PLATFORMS: Final = [Platform.FAN, Platform.SENSOR, Platform.BUTTON]

CONF_POWER_SENSOR: Final = "power_sensor"

# The infrared transmitter is a Home Assistant `infrared` platform emitter
# entity (domain `infrared`), the platform introduced in HA 2026.4 and used
# by the built-in Dyson Infrared integration. Fan commands are sent as
# genuine Dyson Cool protocol codes from the `infrared-protocols` library,
# not free-text device/command pairs.
CONF_INFRARED_EMITTER_ENTITY_ID: Final = "infrared_emitter_entity_id"

# Each of the four relative commands this integration understands is backed
# by one real Dyson Cool IR code (see infrared_protocols.codes.dyson.cool.
# DysonCoolCode). The physical remote reuses the same code every time a
# button is pressed, so each slot maps to exactly one code, chosen by the
# user during setup.
CONF_POWER_TOGGLE_CODE: Final = "power_toggle_code"
CONF_OSCILLATION_TOGGLE_CODE: Final = "oscillation_toggle_code"
CONF_SPEED_UP_CODE: Final = "speed_up_code"
CONF_SPEED_DOWN_CODE: Final = "speed_down_code"

COMMAND_CODE_KEYS: Final = (
    CONF_POWER_TOGGLE_CODE,
    CONF_OSCILLATION_TOGGLE_CODE,
    CONF_SPEED_UP_CODE,
    CONF_SPEED_DOWN_CODE,
)

# Raw IR timings (in microseconds) used to encode every Dyson Cool command
# above - see .ir_codes.ConfigurableDysonCoolCommand. These are Options,
# not initial setup data, since they're a device-specific tuning knob
# separate from which entity/codes to use.
#
# Whether they're actually used depends on CONF_IR_TIMING_MODE: "system"
# uses infrared-protocols' own DysonCoolCommand (published-spec timings,
# 850us/1660us) unmodified; "custom" uses the six fields below.
CONF_IR_TIMING_MODE: Final = "ir_timing_mode"
IR_TIMING_MODE_SYSTEM: Final = "system"
IR_TIMING_MODE_CUSTOM: Final = "custom"
DEFAULT_IR_TIMING_MODE: Final = IR_TIMING_MODE_SYSTEM

CONF_IR_HEADER_MARK: Final = "ir_header_mark"
CONF_IR_HEADER_SPACE: Final = "ir_header_space"
CONF_IR_BIT_MARK: Final = "ir_bit_mark"
CONF_IR_ZERO_SPACE: Final = "ir_zero_space"
CONF_IR_ONE_SPACE: Final = "ir_one_space"
CONF_IR_FOOTER_MARK: Final = "ir_footer_mark"

# The optional feedback-burst helper is not part of the Dyson protocol; it
# runs an arbitrary Home Assistant action (e.g. against a power meter), so it
# keeps the generic action-sequence approach rather than a Dyson IR code.
CONF_FEEDBACK_BURST_ACTION: Final = "feedback_burst_action"

CONF_MAX_ATTEMPTS: Final = "max_attempts"
CONF_IR_SEND_INTERVAL: Final = "ir_send_interval"
CONF_STABILITY_TIMEOUT_SECONDS: Final = "stability_timeout_seconds"
CONF_CALIBRATION_MODE: Final = "calibration_mode"
CONF_RESTORE_DEFAULT_POWER_TABLE: Final = "restore_default_power_table"


class CalibrationMode(StrEnum):
    """Available automatic calibration strategies."""

    ENDPOINTS = "endpoints"
    FULL = "full"


DEFAULT_MAX_ATTEMPTS: Final = 1
DEFAULT_IR_SEND_INTERVAL: Final = 0.35
DEFAULT_CALIBRATION_MODE: Final = CalibrationMode.ENDPOINTS
MIN_IR_SEND_INTERVAL: Final = 0.05
MAX_IR_SEND_INTERVAL: Final = 3.0
MIN_STABILITY_TIMEOUT_SECONDS: Final = 5.0
MAX_STABILITY_TIMEOUT_SECONDS: Final = 300.0

# Bounds for the configurable IR timing fields (microseconds). Generous
# since exact values depend entirely on the physical remote being matched.
MIN_IR_TIMING_MICROSECONDS: Final = 0
MAX_IR_TIMING_MICROSECONDS: Final = 10000

# This integration controls non-heating Dyson fans. A reading above this limit is
# treated as a broken/wrong feedback source instead of being decoded to the
# nearest fan signature.
MAX_SANE_POWER_WATTS: Final = 100.0
POWER_TABLE_DECIMAL_PLACES: Final = 2

SPEED_COUNT: Final = 10
STABLE_REPORTS_REQUIRED: Final = 3

# Fallback path for report-on-change power sensors (e.g. some Zigbee plugs)
# that stay silent while the reading is unchanged instead of repeating it.
# If the current candidate reading has held, uncontradicted, for this long,
# accept it as stable even without STABLE_REPORTS_REQUIRED separate reports.
# Checked on a periodic timer since a silent sensor produces no events to
# hook this off of. User-configurable via CONF_STABILITY_TIMEOUT_SECONDS;
# this is only the fallback used when that option is unset.
DEFAULT_STABILITY_TIMEOUT_SECONDS: Final = 45.0
STABILITY_TIMEOUT_CHECK_INTERVAL_SECONDS: Final = 10.0
POST_COMMAND_SETTLE_SECONDS: Final = 1.0
FEEDBACK_TIMEOUT_SECONDS: Final = 15.0
FEEDBACK_BURST_TIMEOUT_SECONDS: Final = 5.0
DIAGNOSTICS_UPDATE_INTERVAL_SECONDS: Final = 5.0
EVENT_CALIBRATION_FINISHED: Final = f"{DOMAIN}_calibration_finished"

# Extra time added on top of the stability timeout when waiting for post-command
# feedback or a calibration measurement. The timeout-based stability path can
# never fire inside a window shorter than the timeout itself, and report-on-change
# sensors may also take several seconds to publish their first post-command
# reading, independent of the stability timeout.
FEEDBACK_TIMEOUT_BUFFER_SECONDS: Final = 20.0
PERSIST_DELAY_SECONDS: Final = 5.0

STORAGE_VERSION: Final = 1
STORAGE_KEY_PREFIX: Final = f"{DOMAIN}.state"


class ControllerPhase(StrEnum):
    """Possible states of the feedback controller."""

    INITIALIZING = "initializing"
    IDLE = "idle"
    SENDING = "sending"
    WAITING_FEEDBACK = "waiting_feedback"
    CALIBRATING = "calibrating"
    ERROR = "error"


STATE_INITIALIZING: Final = ControllerPhase.INITIALIZING
STATE_IDLE: Final = ControllerPhase.IDLE
STATE_SENDING: Final = ControllerPhase.SENDING
STATE_WAITING_FEEDBACK: Final = ControllerPhase.WAITING_FEEDBACK
STATE_CALIBRATING: Final = ControllerPhase.CALIBRATING
STATE_ERROR: Final = ControllerPhase.ERROR

CALIBRATION_INITIAL_COMMANDS: Final = 15
CALIBRATION_IR_SEND_INTERVAL_SECONDS: Final = 1.0
CALIBRATION_PROBE_COMMANDS: Final = 2
CALIBRATION_UNCHANGED_PROBES: Final = 2
CALIBRATION_MAX_PROBES: Final = 6
CALIBRATION_MEASUREMENT_MIN_SAMPLES: Final = 3
CALIBRATION_MEASUREMENT_FAST_SAMPLES: Final = 5
CALIBRATION_SLOW_REPORT_INTERVAL_SECONDS: Final = 5.0
CALIBRATION_MIN_OBSERVATION_SECONDS: Final = 2.0
# Allows three fresh reports even when a meter updates only once every 10 seconds
# and the measurement starts immediately after one of its scheduled reports.
CALIBRATION_MEASUREMENT_TIMEOUT_SECONDS: Final = 35.0
CALIBRATION_MEASUREMENT_SETTLE_SECONDS: Final = 1.0
CALIBRATION_POWER_CYCLE_OFF_SECONDS: Final = 3.0
CALIBRATION_STABILITY_FLOOR_WATTS: Final = 0.6
CALIBRATION_STABILITY_RATIO: Final = 0.025
CALIBRATION_OUTLIER_FLOOR_WATTS: Final = 0.2
CALIBRATION_OUTLIER_RATIO: Final = 0.01
CALIBRATION_OUTLIER_MAD_MULTIPLIER: Final = 4.4478
CALIBRATION_ENDPOINT_CHANGE_FLOOR_WATTS: Final = 0.8
CALIBRATION_ENDPOINT_CHANGE_RATIO: Final = 0.02
CALIBRATION_FULL_STEP_FLOOR_WATTS: Final = 0.5
CALIBRATION_FULL_STEP_REFERENCE_RATIO: Final = 0.3
CALIBRATION_OSCILLATION_DELTA_MIN_WATTS: Final = 0.5
CALIBRATION_OSCILLATION_DELTA_MAX_WATTS: Final = 10.0
CALIBRATION_RESTORE_TIMEOUT_SECONDS: Final = 60.0

# How close to the per-measurement deadline (calibration_measurement_timeout_
# seconds) a measurement may get before falling back to a best-effort median
# of whatever partial, non-silent, non-fully-stable samples arrived. Covers
# sensors that report somewhat often but never quite settle into 5 tightly
# clustered readings (e.g. genuinely noisier draw at high fan speed) - a
# case neither the strict median nor the total-silence fallback handles.
CALIBRATION_BEST_EFFORT_MARGIN_SECONDS: Final = 3.0


def power_signature_key(speed: int, oscillating: bool) -> str:
    """Return the options key for a power signature."""
    suffix = "oscillating" if oscillating else "stationary"
    return f"power_speed_{speed}_{suffix}"


CONF_POWER_OFF: Final = "power_off"
CONF_POWER_OSCILLATION_DELTA: Final = "power_oscillation_delta"

DEFAULT_POWER_OFF: Final = 1.2
DEFAULT_POWER_OSCILLATION_DELTA: Final = 2.9
DEFAULT_POWER_SIGNATURES: Final[dict[tuple[int, bool], float]] = {
    (1, False): 4.8,
    (1, True): 7.7,
    (2, False): 6.5,
    (2, True): 9.3,
    (3, False): 9.7,
    (3, True): 12.5,
    (4, False): 13.0,
    (4, True): 16.0,
    (5, False): 18.2,
    (5, True): 21.1,
    (6, False): 22.8,
    (6, True): 25.7,
    (7, False): 28.5,
    (7, True): 31.2,
    (8, False): 35.3,
    (8, True): 38.3,
    (9, False): 43.3,
    (9, True): 46.3,
    (10, False): 52.2,
    (10, True): 55.2,
}
