class FileReader:

    @staticmethod
    def read(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        print(f"Read file at {file_path}, length = {content.__len__()}")

        return content