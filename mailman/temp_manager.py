
class TempMan:
    _instance = None
    data = dict()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True

    def get(self, *args) -> dict:
        """
            returns the value found at the specified location in the dict.\n
            pass the location's path keys in the `args`.
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
