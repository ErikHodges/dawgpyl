from termcolor import colored
from termcolor._types import Color
from IPython.display import Markdown, display
from pprint import pprint

COLORS = [
    "blue",
    "light_blue",
    "cyan",
    "light_cyan",
    "yellow",
    "light_yellow",
    "green",
    "light_green",
    "magenta",
    "light_magenta",
    "red",
    "light_red",
    "black",
    "dark_grey",
    "grey",
    "light_grey",
    "white",
]

NL = "\n" + "-" * 80 + "\n"


def print_heading(title_text: str, color: Color = "cyan") -> None:
    """Print a heading with a title enclosed in dashes.

    Args:
        title_text (str): The title text to be printed.
        color (str, optional): The color of the heading. Defaults to "cyan".

    Returns:
        None
    """
    title_length = len(title_text)
    title_bar = "----" + ("-" * title_length) + "----"
    print(colored(title_bar, color, attrs=["bold"], force_color=True))
    print(colored(f"    {title_text}", color, attrs=["bold"], force_color=True))
    print(colored(title_bar, color, attrs=["bold"], force_color=True))
    return None


def print_dict(
    dict2print: dict | str, colors: list[Color] | Color = ["cyan", "light_blue"], width: int = 80
) -> None:
    """Print a dictionary with colored keys and values.

    Args:
        dict2print (dict): The dictionary to be printed.
        colors (list, optional): The color of the keys and values. Defaults to ["cyan","light_blue"].
        width (int,optional): The width of the output. Defaults to 80.
    Returns:
        None
    """
    if isinstance(colors, str):
        colors = [colors]
    if isinstance(colors, list) and len(colors) == 1:
        colors.append(colors[0])

    try:
        if not isinstance(dict2print, str):
            if not ((hasattr(dict2print, "items")) and (callable(dict2print.items))):
                dict2print = dict2print.__dict__
            if isinstance(dict2print, dict):
                for k, v in dict2print.items():
                    k = k + ":"
                    printkey = colored(f"{k:<10}", color=colors[0], attrs=["bold"])
                    printval = colored(f"{v}", color=colors[1])

                    print(printkey, printval)
    except:
        pprint(dict2print, width=width)


def map_member_colors(member_names: list, color_names: list) -> dict:
    """Map member names to colors.

    Args:
        member_names (list): A list of member names.
        color_names (list): A list of color names.

    Returns:
        dict: A dictionary mapping member names to colors.
    """
    member_colors = {}
    for idx, member_name in enumerate(member_names):
        member_colors[member_name] = color_names[idx]
    return member_colors


def print_md(markdown_str: object):
    return Markdown(markdown_str)


def eprint(printable: object, color: list[Color] | Color = ["blue", "green"], width=80) -> None:
    """Pretty print a given object with no sorting,

    Args:
        printable (object): The object to be pretty printed.

    Returns:
        None
    """
    if type(color) == str:
        color = [color]
    try:
        display(print_md(printable))
    except Exception:
        try:
            print_dict(printable, color)
        except Exception:
            print(
                colored(
                    pprint(printable, sort_dicts=False, width=width), color=color, force_color=True
                )
            )


# test_str = "This is a basic string."
# test_md = "**This is a Markdown string.**"
# test_dict = {"positive": {"yes": "yup"}, "negative": {"no": "nope"}}

# print("-" * 80, "\n" + "print")
# print(test_str)
# print(test_md)
# print(test_dict)

# print("-" * 80, "\n" + "pprint")
# pprint(test_str)
# pprint(test_md)
# pprint(test_dict)


# print("-" * 80, "\n" + "print_dict")
# print_dict(test_str, ["light_cyan", "green"])
# print_dict(test_md)
# print_dict(test_dict, ["light_cyan", "green"])
# print_dict(test_dict, ["green"])
# print_dict(test_dict, "blue")

# print("-" * 80, "\n" + "eprint")
# eprint(test_str)
# eprint(test_md)
# eprint(test_dict, ["red", "blue"])
