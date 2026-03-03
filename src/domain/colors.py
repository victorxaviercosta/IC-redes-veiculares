"""
domain/colors.py
------------------------------

Defines some ANSI escape color codes.
"""

BOLD        = "\033[1m"
DIM         = "\033[2m"
ITALIC      = "\033[3m"
UNDERLINE   = "\033[4m"
BLINKING    = "\033[5m"

RESET = "\033[0m" # Code to reset styles and colors

#=== Foreground Color codes ===
FG_BLACK   = "\033[90m"
FG_RED     = "\033[91m"
FG_GREEN   = "\033[92m"
FG_YELLOW  = "\033[93m"
FG_BLUE    = "\033[94m"
FG_MAGENTA = "\033[95m"
FG_CYAN    = "\033[96m"
FG_WHITE   = "\033[97m"

#=== Background Color codes ===
BG_BLACK   = "\033[100m"
BG_RED     = "\033[101m"
BG_GREEN   = "\033[102m"
BG_YELLOW  = "\033[103m"
BG_BLUE    = "\033[104m"
BG_MAGENTA = "\033[105m"
BG_CYAN    = "\033[106m"
BG_WHITE   = "\033[107m"
