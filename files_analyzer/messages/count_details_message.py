def count_details_message(
        directory_count: int,
        file_count: int,
        block_device_count: int,
        char_device_count: int,
        junction_count: int,
        socket_count: int,
        symlink_count: int,
        fifo_count: int,
        unknown_count: int,
        total: int
) -> str:
    text = f"""
=======================
Directory count: {directory_count}
File count: {file_count}
Block device count: {block_device_count}
Char device count: {char_device_count}
Junction count: {junction_count}
Socket count: {socket_count}
Symlink count: {symlink_count}
Fifo count: {fifo_count}

Unknown objects count: {unknown_count}
=======================

Total: {total}
"""

    return text.strip()