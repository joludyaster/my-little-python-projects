from pathlib import Path
from data import File
from enums import FileEnums
import datetime
import csv
import os
from messages.count_details_message import count_details_message

def print_and_log(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"

    print(log_entry)

    folder = "logs"
    random_file_name = "logs.log"

    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/{random_file_name}", "a") as file:
        file.write(log_entry + "\n")

class FilesAnalyzer:
    def __init__(self, path_to_directory: Path):
        self.path_to_directory = path_to_directory

        self._file_storage = {}
        self._extension_storage = {}

        self._directory_count = 0
        self._file_count = 0

        self._block_device_count = 0
        self._char_device_count = 0

        self._junction_count = 0
        self._socket_count = 0

        self._symlink_count = 0
        self._fifo_count = 0

        self._unknown_count = 0

        self._visited_dirs = set()

    def _add_file_to_storage(
            self,
            file: File
    ) -> bool:
        try:
            get_file = self._file_storage.get(file.path_to_file)
            if get_file:
                print_and_log(f"There cannot be two identical filenames.\nSkipping: {file.filename}")
                return False

            self._file_storage.update(
                {
                    file.path_to_file: {
                        FileEnums.FILENAME: file.filename,
                        FileEnums.EXTENSION: file.extension,
                        FileEnums.SIZE: file.size
                    }
                }
            )

            self._add_extension_to_storage(
                extension_name=file.extension
            )

            return True
        except Exception as e:
            print_and_log(f"Error occurred when adding a file. {e}")
            print()
            return False

    def _add_extension_to_storage(self, extension_name: str, quantity: int = 1) -> bool:
        try:
            get_key = self._extension_storage.get(extension_name, 0)
            self._extension_storage[extension_name] = get_key + quantity
            return True
        except Exception as e:
            print_and_log(f"Couldn't add extension to the storage. {e}")
            return False

    def _handle_directory(self, path_to_directory: Path):

        try:
            stat = path_to_directory.stat()
            key = (stat.st_ino, stat.st_dev)
            if key in self._visited_dirs:
                return
            self._visited_dirs.add(key)
        except Exception as e:
            print_and_log(f"Could not stat {path_to_directory}: {e}")
            return

        try:
            paths = path_to_directory.iterdir()
        except PermissionError:
            print_and_log(f"Permission denied: {path_to_directory}")
            return

        self._directory_count += 1

        for path in paths:
            print_and_log(f"Path to analyze: {path}")
            if path.is_dir():
                self._handle_directory(path_to_directory=path)
            else:
                if path.is_symlink():
                    self._symlink_count += 1
                elif path.is_block_device():
                    self._block_device_count += 1
                elif path.is_char_device():
                    self._char_device_count += 1
                elif path.is_fifo():
                    self._fifo_count += 1
                elif path.is_junction():
                    self._junction_count += 1
                elif path.is_socket():
                    self._socket_count += 1
                elif path.is_file():
                    self._file_count += 1
                else:
                    self._unknown_count += 1

                self._handle_file(filename=path.name, path_to_file=path)

    def _handle_file(self, filename: str, path_to_file: Path):
        extension = path_to_file.suffix if path_to_file.suffix != "" else "No extension file"
        try:
            size = path_to_file.stat().st_size
        except (FileNotFoundError, PermissionError, Exception):
            print_and_log("Couldn't read the size of the file. Settings to 0.")
            size = 0

        file = File(
            filename=filename,
            path_to_file=path_to_file,
            extension=extension,
            size=size
        )
        self._add_file_to_storage(file=file)

    def _calculate_total(self) -> int:
        return sum(
            [
                self._directory_count,
                self._file_count,
                self._block_device_count,
                self._char_device_count,
                self._junction_count,
                self._socket_count,
                self._symlink_count,
                self._fifo_count,
                self._unknown_count
            ]
        )

    def _display_count_details(self) -> None:
        text = count_details_message(
            directory_count=self._directory_count,
            file_count=self._file_count,
            block_device_count=self._block_device_count,
            char_device_count=self._char_device_count,
            junction_count=self._junction_count,
            socket_count=self._socket_count,
            symlink_count=self._symlink_count,
            fifo_count=self._fifo_count,
            unknown_count=self._unknown_count,
            total=self._calculate_total()
        )
        print(text)

    def _write_data_to_file(self):
        random_file_name = int(datetime.datetime.now().timestamp())

        os.makedirs("output", exist_ok=True)
        output_directory = f"output/file{random_file_name}.csv"

        with open(output_directory, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(
                ["Directories count",
                 "File count",
                 "Block device count",
                 "Char device count",
                 "Junction count",
                 "Socket count",
                 "Symlink count",
                 "Fifo count",
                 "Unknown count",
                 "Total count"
                 ]
            )

            writer.writerow(
                [
                    self._directory_count,
                    self._file_count,
                    self._block_device_count,
                    self._char_device_count,
                    self._junction_count,
                    self._socket_count,
                    self._symlink_count,
                    self._fifo_count,
                    self._unknown_count,
                    self._calculate_total()
                ]
            )

            writer.writerow([])

            writer.writerow(['Extension', 'Count'])
            for ext, count in sorted(self._extension_storage.items()):
                writer.writerow([ext, count])

            writer.writerow([])
            writer.writerow(
                [
                    'Path',
                    'Filename',
                    'Extension',
                    'Size'
                ]
            )

            for file_path, data in self._file_storage.items():
                writer.writerow(
                    [
                        file_path,
                        data[FileEnums.FILENAME],
                        data[FileEnums.EXTENSION],
                        data[FileEnums.SIZE]
                    ]
                )

    def analyze_files(self):
        self._handle_directory(
            path_to_directory=self.path_to_directory
        )

        self._write_data_to_file()
        self._display_count_details()

def main():
    try:
        path_to_directory = Path(str(input("Enter a path to directory: ")))

        if not path_to_directory.is_dir():
            print_and_log("Path should point to a directory.")
            return main()

        files_analyzer = FilesAnalyzer(path_to_directory=path_to_directory)
        files_analyzer.analyze_files()
    except FileNotFoundError:
        print_and_log("Invalid path. Try again.")


if __name__ == "__main__":
    main()
