import random
from pystyle import Write, Colors

gradients = [
    Colors.red_to_yellow, Colors.red_to_purple, Colors.red_to_blue,
    Colors.yellow_to_red, Colors.yellow_to_green, Colors.green_to_yellow,
    Colors.green_to_cyan, Colors.green_to_blue, Colors.cyan_to_green,
    Colors.cyan_to_blue, Colors.blue_to_cyan, Colors.blue_to_purple,
    Colors.blue_to_red, Colors.purple_to_blue, Colors.purple_to_red
]

def get_random_gradient():
    return random.choice(gradients)

def print_log(text, color=None, interval=0.05):
    if color is None:
        color = get_random_gradient()
    Write.Print(text, color, interval=interval)

def input_log(text, color=None, interval=0.05):
    if color is None:
        color = Colors.cyan_to_blue
    return Write.Input(text, color, interval=interval)
