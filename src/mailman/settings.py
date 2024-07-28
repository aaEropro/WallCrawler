import yaml


class Settings:
    """
    manages global; persistent settings.
    on initialization reads data from `datafile.yaml`.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True
        with open('datafile.yml', encoding="utf-8", mode="r") as file:
            self.data = yaml.safe_load(file)

    def get(self, *args) -> any:
        """
            returns the value found at the specified location in the dict.\n
            pass the location's path keys in the `args`.
            :returns: the string value or `None`.
        """
        searched: dict = self.data

        for item in args:
            if type(searched) is dict: 
                searched = searched.get(item, None)

        return searched

    def update(self, data, *args) -> None:
        """
            updates the value found at the specified location in the dict.\n
            pass the location's path keys in the `args` and the value in `data`.
        """
        current: dict = self.data

        for key in args[:-1]:
            if type(current) is dict:
                current = current.get(key, None)

        if type(current) is dict:
            current[args[-1]] = data

        with open('datafile.yml', 'w') as file:
            yaml.safe_dump(self.data, file)
    

if __name__ == '__main__':
    instance = Settings()

    Settings().update('/test/path', 'last-opened', 'input_dir')

    print(f'got setting {Settings().data}')
