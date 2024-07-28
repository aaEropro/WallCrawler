from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import sys
from src.mailman.settings import Settings
from src.mailman.temp_manager import TempMan
import os
from src.processor.structure import Structure


class LineEdit(QLineEdit):

    def mousePressEvent(self, a0: QMouseEvent) -> None:

        data = QFileDialog.getExistingDirectory(self, "Input Directory")
        if data != '':
            self.dir_path = data
            self.setText(self.dir_path)

        return super().mousePressEvent(a0)


class ErrorsWidget(QFrame):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("ErrorsWidget { border: 2px solid red; }")


    def submit_errors(self, errors:list):

        for item in errors:
            self.layout().addWidget(QLabel(text=item))


class ItemsTree(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)

        # self.setReadOnly(True)
        # self.setStyleSheet('backgorund: ')


    def submit_tree(self, tree:dict):
        text = '\nHEAD\n'
        # text = f'{"HEAD": >12}\n'
        for item in tree['head']:
            if tree['head'][item]:
                text += f'|--{item}\n'

        text += '\nBODY\n'
        ch = [item.split('-')[0] for item in sorted(tree['body'])]
        if len(ch) > 4:
            text += f'|--{ch[0]}\n|--{ch[1]}\n|--{ch[2]}\n|  ...\n|--{ch[-1]}\n'
        
        text += '\nBOTTOM\n'
        # text += f'{"BOTTOM": >12}\n'
        for item in tree['bottom']:
            if tree['bottom'][item]:
                text += f'|--{item}\n'

        text += '\nUNRECOGNIZED\n'
        for item in tree['unrecognized']:
            text += f'|--{item}\n'

        # print(text)
        self.setText(text)


class Widget(QWidget):
    close_signal = None 
    confirmed = False

    def __init__(self, parent):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())

        # MASTER CONTAINER
        self.master_cont = QWidget()
        self.master_cont.setLayout(QVBoxLayout())
        self.master_cont.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.master_cont.layout().setAlignment(self.master_cont, Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self.master_cont)

        # INDIVIDUAL CONTAINERS
        self.cont1 = QWidget()
        self.cont1.setLayout(QHBoxLayout())
        self.master_cont.layout().addWidget(self.cont1)
        # self.master_cont.layout().setAlignment(self.cont1, Qt.AlignmentFlag.AlignCenter)
        self.cont2 = QWidget()
        self.cont2.setLayout(QHBoxLayout())
        self.master_cont.layout().addWidget(self.cont2)
        # self.master_cont.layout().setAlignment(self.cont2, Qt.AlignmentFlag.AlignCenter)

        # LABELS
        input_folder_label = QLabel('FOLDER IN')
        input_folder_label.setMinimumWidth(120)
        self.cont1.layout().addWidget(input_folder_label)
        output_folder_label = QLabel('FOLDER OUT')
        output_folder_label.setMinimumWidth(120)
        self.cont2.layout().addWidget(output_folder_label)

        # INPUTS
        self.input_folder_input = LineEdit()
        self.input_folder_input.setMinimumWidth(400)
        self.input_folder_input.setReadOnly(True)
        self.input_folder_input.textChanged.connect(lambda x: self.pathChange(x, 'input_dir'))
        self.cont1.layout().addWidget(self.input_folder_input)
        self.output_folder_input = LineEdit()
        self.output_folder_input.setMinimumWidth(400)
        self.output_folder_input.setReadOnly(True)
        self.output_folder_input.textChanged.connect(lambda x: self.pathChange(x, 'output_dir'))
        self.cont2.layout().addWidget(self.output_folder_input)

        # ERRORS WIDGET
        # self.errors = ErrorsWidget()
        # self.master_cont.layout().addWidget(self.errors)

        # ITEMS TREE
        # self.tree = ItemsTree()
        # self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.master_cont.layout().addWidget(self.tree)
        # self.master_cont.layout().setAlignment(self.tree, Qt.AlignmentFlag.AlignHCenter)

        # CONFIRM
        self.confirm_button = QPushButton()
        self.confirm_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.confirm_button.setText("Confirm")
        self.confirm_button.clicked.connect(self.callback)
        self.master_cont.layout().addWidget(self.confirm_button)

        # LOAD LAST OPENED FOLDERS
        if Settings().get('settings', 'use-last-opened'):
            input_dir = Settings().get('lastopened', 'input_dir')
            if input_dir != None and os.path.isdir(input_dir):
                self.input_folder_input.dir_path = input_dir
                self.input_folder_input.setText(input_dir)
            output_dir = Settings().get('lastopened', 'output_dir')
            if output_dir != None and os.path.isdir(os.path.dirname(output_dir)):
                self.output_folder_input.dir_path = output_dir
                self.output_folder_input.setText(output_dir)

    def pathChange(self, data, tm_id):
        """
        updates the tree and error bord when the path to the input folder is changed.
        :param data: path to the folder.
        :param tm_id: TempMan id.
        :return: None.
        """
        TempMan().update(data, tm_id)

        if tm_id == 'input_dir':
            inst = Structure()
            inst.s(data)
            # print(inst.errors)
            # self.errors.submit_errors(inst.errors)
            # self.tree.submit_tree(inst.structure)

    def callback(self):
        """
        destroyer method.
        :return: None
        """
        self.confirmed = True
        Settings().update(self.input_folder_input.text(), 'lastopened', 'input_dir')
        Settings().update(self.output_folder_input.text(), 'lastopened', 'output_dir')
        self.close_signal()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_instance = Widget(self)
        self.widget_instance.close_signal = self.close
        self.setCentralWidget(self.widget_instance)

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.widget_instance.confirmed:
            return super().closeEvent(a0)
        else:
            print(f'input not confirmed.\nexiting...\n')
            sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    instance.show()

    sys.exit(app.exec())