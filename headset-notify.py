#!/usr/bin/python3
import logging
import re
import subprocess
import time

import psutil

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def check_headset() -> tuple[str | None, int | None, bool]:
    """Check the status of the wireless headset.

    Uses headsetcontrol to query the device status and battery information.

    Returns:
        tuple: Contains (device_name, battery_level, battery_available)
        where:
            - device_name (str | None): Name of the detected device or None if not found.
            - battery_level (int | None): Battery percentage or None if unavailable.
            - battery_available (bool): True if battery status is available.
    """

    try:
        result = subprocess.run(
            ["headsetcontrol", "-b"], capture_output=True, text=True
        )
        output = result.stdout.strip()

        # Check if device is found
        device_match = re.search(r"Found (.*?)!", output)
        if not device_match:
            return None, None, False

        device_name = device_match.group(1)

        # Check battery status
        battery_available = "BATTERY_AVAILABLE" in output

        # Get battery level if available
        battery_match = re.search(r"Level: (\d+)%", output)
        battery_level = int(battery_match.group(1)) if battery_match else None

        return device_name, battery_level, battery_available

    except subprocess.CalledProcessError:
        return None, None, False
    except Exception as e:
        logging.error(f"Error checking headset: {e}")
        return None, None, False


def send_notification(title: str, message: str) -> None:
    """Send a desktop notification using notify-send.

    Args:
        title (str): The title of the notification.
        message (str): The body text of the notification.

    Raises:
        Exception: If notification sending fails.
    """

    try:
        subprocess.run(
            ["notify-send", "--icon=audio-headset", "--urgency=normal", title, message]
        )
    except Exception as e:
        logging.error(f"Error sending notification: {e}")


def get_cpu_percent() -> float:
    """Get the current CPU usage percentage.

    Return:
        float: Current CPU usage as a percentage
    """

    return psutil.cpu_percent(interval=None)


def adaptive_sleep() -> float:
    """Calculate sleep duration based on CPU usage.

    Adjusts the polling interval based on current CPU load to reduce system impact.

    Returns:
        float: Sleep duration in seconds (0.5 for high CPU, 0.1 for low CPU)
    """

    cpu_percent = get_cpu_percent()
    if cpu_percent > 20:
        return 0.5
    return 0.1


def main() -> None:
    """Main program loop for monitoring wireless headset status.

    Continuously monitors the headset's connection status and battery level,
    sending desktop notifications when the device connects or disconnects.
    Implements rate limiting and adaptive polling based on CPU usage.
    """

    logging.info("Starting wireless headset monitor...")
    last_available = False
    last_device_name = None
    last_check = 0
    min_time_between_checks = 0.1

    while True:
        try:
            current_time = time.time()

            # Rate limiting
            if current_time - last_check < min_time_between_checks:
                time.sleep(0.01)  # Very short sleep if checking too frequently
                continue

            device_name, battery_level, battery_available = check_headset()
            last_check = current_time

            # State transitions based on battery availability
            if not last_available and battery_available:
                send_notification(
                    "Headset Turned On",
                    f"Device: {device_name}\nBattery: {battery_level}%",
                )
                last_available = True
                last_device_name = device_name
            elif last_available and not battery_available and device_name:
                send_notification(
                    "Headset Turned Off", f"Device '{last_device_name}' powered down"
                )
                last_available = False

        except Exception as e:
            logging.error(f"Error in main loop: {e}")

        sleep_time = adaptive_sleep()
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
