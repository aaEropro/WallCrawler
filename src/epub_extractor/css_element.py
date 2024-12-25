class CSSElement:
    """
    stores a CSS element, defined by `name` and `class`.
    """
    def __init__(self, class_name: str):
        self.name = None
        self.css_class = None

        elements = class_name.split(".")

        if len(elements) > 1:
            self.css_class = elements[1]

        self.name = elements[0]


    def __eq__(self, other):
        if isinstance(other, CSSElement):
            return self.name == other.name or   (self.css_class and self.css_class == other.css_class)
        return False


    def __str__(self):
        if self.css_class:
            return self.name + "." + self.css_class
        return self.name


    def __repr__(self):
        return f'CSSElement({self.name}{"." + self.css_class if self.css_class else ""})'


    def getName(self) -> str:
        return self.name


    def getClass(self) -> str:
        return self.css_class


    def hasClass(self) -> bool:
        if self.css_class:
            return True
        return False