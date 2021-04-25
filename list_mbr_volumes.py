import argparse
import os
from os import path

from kaitaistruct import ValidationNotEqualError

from kaitai_parse.mbr_partition_table import MbrPartitionTable

MBR_BYTES_SEC_NUM = 512

TYPE_EXTENDED = 0x5

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List volumes from raw image (supports only MBR)')
    parser.add_argument('path', metavar='image', type=str,
                        help='path to raw image file')

    args = parser.parse_args()
    absolute_image_path = path.abspath(args.path)

    stream = open(absolute_image_path, 'rb')
    vol_list, rel_offsets_to_check = [], [0]
    current_offset = 0

    while len(rel_offsets_to_check) > 0:
        rel_offset = rel_offsets_to_check.pop()
        stream.seek(rel_offset, os.SEEK_CUR)
        current_offset += rel_offset
        try:
            mbr_table = MbrPartitionTable.from_io(stream)
        except ValidationNotEqualError:
            exit(1)
        stream.seek(current_offset)
        for volume in mbr_table.partitions:
            if volume.lba_start != 0 and volume.partition_type != TYPE_EXTENDED:
                # Save LBA from current offset to indicate real starting LBA for ext. partitions
                vol_list.append((volume, current_offset // MBR_BYTES_SEC_NUM))
            elif volume.partition_type == TYPE_EXTENDED:
                # Extended partitions use relative offsets in their LBA fields
                rel_offsets_to_check.append(volume.lba_start * MBR_BYTES_SEC_NUM)

    stream.close()

    for index, (volume, lba) in enumerate(vol_list):
        print(f"Volume no. {index + 1} at LBA {lba + volume.lba_start} - type {volume.partition_type}")
