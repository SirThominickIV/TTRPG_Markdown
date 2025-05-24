if [ -d ".venv" ]; then
    echo "Virtual environment '.venv' already exists. Aborting."
    return 1
fi

python3.8 -m venv ".venv"

source "./.venv/bin/activate"
pip install -U pip

if [ -f "requirements.txt" ]; then
    pip install -r ./requirements.txt
fi