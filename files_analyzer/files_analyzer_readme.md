# Files Analyzer
A Python script that analyzes files in a directory and its subdirectories.

# Usage
To run the script, first create isolated virtual environment and install the required packages using the following commands:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Then, run the script with the path to the directory you want to analyze:
```bash
python main.py /path/to/directory
```
The script will analyze the files in the directory and its subdirectories, and generate a CSV file with the results.