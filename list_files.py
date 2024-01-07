import logging
import os
import sys

path = 'your-local-path'

def main():
    logging.basicConfig(level=logging.INFO)
    list_files(path, [validate_is_jpg, validate_name])

def validate_name(file_path, name = '1'):
    filename = get_filename_by_path(file_path)
    flag = filename == name

    # todo 这个是特殊逻辑，需要根据实际情况调整
    if not flag:
        rename(file_path)

    return True

def get_filename_by_path(file_path):
    basename = os.path.basename(file_path)
    filename, _ = os.path.splitext(basename)
    return filename

def rename(file_path, new_name_with_extension ='1.jpg'):
    new_file_path = os.path.join(os.path.dirname(file_path), new_name_with_extension)
    logging.info('rename %s to %s', file_path, new_file_path)
    os.rename(file_path, new_file_path)
    return new_file_path

def validate_is_jpg(file_path):
    return file_path.lower().endswith('.jpg')

def list_files(path, validate_func=[]):
    for root, directories, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)

            for func in validate_func:
                if not func(file_path):
                    logging.error(f"The file does not pass validation: {func.__name__}")
                    sys.exit(1)

if __name__ == '__main__':
    main()