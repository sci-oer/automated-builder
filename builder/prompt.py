### This was modified from https://github.com/tylerdave/prompter


import re
import sys
from typing import Optional, List

try:
    import readline
except:
    if sys.platform == "win32" or sys.platform == "cygwin":
        try:
            from pyreadline3 import Readline
        except:
            pass


def get_input(message: Optional[str] = None) -> str:
    return input(message)


def prompt(
    message: str, default: Optional[str] = None, strip: bool = True, suffix: str = " "
) -> Optional[str]:
    """Print a message and prompt user for input. Return user input."""
    if default is not None:
        prompt_text = "{0} [{1}]{2}".format(message, default, suffix)
    else:
        prompt_text = "{0}{1}".format(message, suffix)

    input_value = get_input(prompt_text)

    if input_value and strip:
        input_value = input_value.strip()

    if not input_value:
        input_value = default

    return input_value


def prompt_list(message: str, strip: bool = True, suffix: str = " ") -> List[str]:
    values: List[str] = []
    content = prompt(message, strip=strip, suffix=suffix)

    while content is not None:
        values.append(content)
        content = prompt(message, strip=strip, suffix=suffix)
    return values


def yesno(message: str, default: Optional[str] = None, suffix: str = " ") -> bool:
    """Prompt user to answer yes or no. Return True for yes and False for
    no."""
    if default == "yes":
        yesno_prompt = "[Y/n]"
    elif default == "no":
        yesno_prompt = "[y/N]"
    elif default == None:
        yesno_prompt = "[y/n]"
    else:
        raise ValueError("default must be 'yes' or 'no', or None.")

    if message != "":
        prompt_text = "{0} {1}{2}".format(message, yesno_prompt, suffix)
    else:
        prompt_text = "{0}{1}".format(yesno_prompt, suffix)

    while True:
        response = get_input(prompt_text).strip()
        if response == "":
            response = default

        if re.match("^(y)(es)?$", response, re.IGNORECASE):
            return True
        elif re.match("^(n)(o)?$", response, re.IGNORECASE):
            return False


def prompt_options(
    message: str, options: List[str], default: Optional[str] = None, suffix: str = ": "
) -> bool:
    """Prompt user to select an option from a list."""
    default_index = 0
    if default == None:
        default_index = 0
    elif default not in options:
        raise ValueError("default must be in the list of options.")
    else:
        default_index = options.index(default)

    prompt_text = f"{message}{suffix}"

    def print_options(index: int, options: List[str]):
        print("options (the default option is marked with a *):")
        for index, value in enumerate(options):
            print(f" {index}{' ' if default_index != index else '*'}. {value}")

    while True:
        print_options(default_index, options)
        response = get_input(prompt_text).strip()

        selection = default_index
        try:
            if response != "":
                selection = int(response)
        except:
            selection = -1

        if selection < 0 or selection > len(options):
            print(
                "Invalid option: {response} must be one of the option numbers in the list."
            )
        else:
            return options[selection]
