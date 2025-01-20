import os
import sys

# Add the base directory to the sys path
def update_sys_path(debug: bool = False) -> None:
    """
    Add the base directory to the sys path
    """

    # abs filepath of current file
    abs_path_current_file = os.path.abspath(__file__)

    if debug:
        print(f"Current file path: {abs_path_current_file}")

    # base directory of current file
    base_dir = os.path.dirname(abs_path_current_file)
    if debug:
        print(f"Base directory: {base_dir}")

    # this should be base path '/Users/silasjohn/Zephyr' for others it will end in 'Zephyr'
    while os.path.basename(base_dir) != 'Zephyr':
        base_dir = os.path.dirname(base_dir)

    if debug:
        print(f"Base Project Directory: {base_dir}")

    # add the base directory to the sys path
    sys.path.append(base_dir)

    if debug:
        print(f"Sys Path Updated: {sys.path}")
        
    return None
