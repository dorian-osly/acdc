set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if [ -f "$DIR/dist/AnimalCrossingDynamicClock" ]; then
    chmod +x "$DIR/dist/AnimalCrossingDynamicClock"
    nohup "$DIR/dist/AnimalCrossingDynamicClock" >/dev/null 2>&1 &
    exit 0
fi

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    if command -v python >/dev/null 2>&1; then
        PYTHON_BIN="python"
    else
        echo "Error: Python 3 is not installed. Please install Python 3 (e.g., sudo apt install python3 or sudo pacman -S python)."
        exit 1
    fi
fi

if [ -d "$DIR/.venv" ]; then
    source "$DIR/.venv/bin/activate"
fi

nohup "$PYTHON_BIN" "$DIR/main.py" >/dev/null 2>&1 &
disown
