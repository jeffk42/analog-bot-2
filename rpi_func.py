is_pi = True

try:
    import RPi.GPIO as gpio
except RuntimeError:
    print("Ignoring lights - Not a Raspberry Pi")
    is_pi = False

lights = {
    'yellow_1' : 19,
    'blue_1' : 26,
    'progress_1' : 22,
    'progress_2' : 10,
    'progress_3' : 9,
    'progress_4' : 11,
    'progress_5' : 5,
    'progress_g1' : 6,
    'progress_g2' : 13
}

all_lights = [19, 26, 22, 10, 9, 11, 5, 6, 13]


def setup_feedback_lights():
    if is_pi:
        gpio.setmode(gpio.BCM)
        gpio.setup(all_lights, gpio.OUT)


def teardown_feedback_light():
    if is_pi:
        gpio.output(all_lights, False)
        gpio.cleanup(all_lights)


def light_solid(light_list):
    if is_pi:
        gpio.output(light_list, True)


def get_light_status(light_list):
    if is_pi:
        return gpio.input(light_list)
    else:
        return False


def light_off(light_list):
    if is_pi:
        gpio.output(light_list, False)


def light_blink(light_list):
    pass
