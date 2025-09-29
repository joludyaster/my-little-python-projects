from dataclasses import dataclass
from pathlib import Path

@dataclass
class File:
    filename: str
    path_to_file: Path
    extension: str
    size: int
