import os


def collect_local_files(local_path: str) -> dict[str, str]:
    """
    Функция для сбора данных о файлах в директории (имя: дата последнего изменения)
    :param local_path:
    :return:
    """
    local_files = os.listdir(local_path)
    files_info = {}
    for file in local_files:
        file_path = os.path.join(local_path, file)
        if os.path.isfile(file_path):
            files_info[file] = os.path.getmtime(file_path)

    return files_info
