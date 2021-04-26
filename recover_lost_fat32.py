import argparse
import mmap
import os
from os import path

from kaitaistruct import ValidationNotEqualError

from kaitai_parse.vfat import Vfat


def check_vfat(vfat: Vfat) -> bool:
    if vfat.boot_sector.bpb.bytes_per_ls not in [512, 1024, 2048, 4096]:
        return False
    if vfat.boot_sector.bpb.ls_per_clus not in [1, 2, 4, 8, 16, 32, 64, 128]:
        return False
    return vfat.boot_sector.size_fat > 0 and vfat.boot_sector.pos_fats > 0 and vfat.boot_sector.bpb.num_fats >= 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List volumes (deleted ones too)')
    parser.add_argument('path', metavar='image', type=str,
                        help='path to raw image file')
    parser.add_argument('--offset', metavar='offset', type=int, default=0,
                        help='offset to start looking')

    args = parser.parse_args()
    absolute_image_path = path.abspath(args.path)

    file = open(absolute_image_path, 'rb')
    file_size = os.path.getsize(absolute_image_path)
    fileno = file.fileno()
    file_map = mmap.mmap(fileno, 0, mmap.MAP_SHARED, mmap.ACCESS_READ)

    file_map.seek(args.offset)
    while sector := file_map.read(512):
        curr_pos = file_map.tell()
        try:
            # Perform simple validation
            vfat = Vfat.from_bytes(sector)
            if not check_vfat(vfat):
                raise ValueError
            file_map.seek(-512, os.SEEK_CUR)
            vfat = Vfat.from_io(file_map)
            file_map.seek(curr_pos - 512)
            # Try to access parsed FAT or root_dir
            vfat.fats
            total_ls = max(vfat.boot_sector.bpb.total_ls_2, vfat.boot_sector.bpb.total_ls_4,
                           vfat.boot_sector.ls_per_fat)
            if total_ls * vfat.boot_sector.bpb.bytes_per_ls > file_size - curr_pos:
                raise ValueError
            print(
                f"Found FAT32 at: {file_map.tell()} of size {total_ls} (in logical sectors) - {vfat.boot_sector.oem_name}")
            file_map.seek(total_ls * vfat.boot_sector.bpb.bytes_per_ls, os.SEEK_CUR)
        except UnicodeDecodeError:
            pass
        except ValidationNotEqualError:
            pass
        except EOFError:
            pass
        except ValueError:
            pass
