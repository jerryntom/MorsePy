import pyttsx3 as tts
from re import match
from ctypes import windll
from platform import system
from sys import argv, exit
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget
from PySide6.QtCore import QEvent

if system() == "Windows":
    myappid = u'jerryntom.python.morseapp.3422'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
else:
    pass


class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window")
        self.setWindowIcon(QtGui.QIcon("resources\\app_img\\icon.png"))
        self.setFixedSize(600, 300)
        self.input = QtWidgets.QTextEdit(self)
        self.input.setGeometry(QtCore.QRect(60, 40, 490, 180))
        self.input.setStyleSheet("font-size: 30px;")
        self.input.setObjectName("field2")
        self.input.setPlaceholderText("Domyślne okno menu - test")
        self.input.horizontalScrollBar().setEnabled(False)
        self.input.setAcceptRichText(False)


class Settings(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.input.setPlaceholderText("Okno ustawień")


class Help(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.input.setPlaceholderText("Okno pomocy")


class About(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.input.setPlaceholderText("Okno informacji o projekcie")


class Report(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report")
        self.input.setPlaceholderText("Okno zgłaszania błędów")


class MorseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.chars_value = dict()
        self.morse_value = dict()

        with open("resources\\data\\values.txt", "r", encoding="UTF-8") as f:
            for line in f.readlines():
                char, value = line.split()

                self.chars_value[char] = value
                value = value.replace('•', '.')
                char = char.lower()
                self.morse_value[value] = char

        self.style_input = """
        color: black;
        background-color: white;
        border: 2px solid black;
        border-radius: 18px;"""

        self.style_button = """
        border: 2px solid black;
        border-radius: 20px;
        color: black;
        """

        self.style_side_btn = """
        border: 2px solid black;
        background-color: white;
        border-radius: 22px;
        color: black;
        """

        self.style_scroll_bar = """
        QScrollBar:vertical {
            border: none;
            background: none;
            height: 0;
            margin: 0 0 0 0;
        }

        QScrollBar::handle:vertical  {
            background: none;
            min-width: 0;
        }

        QScrollBar::add-line:vertical  {
            background: none;
            width: 0;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }"""

        self.field_value = ""
        self.font = QtGui.QFont()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.change_lang_btn = QtWidgets.QPushButton(self.centralwidget)
        self.read1_morse_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop1_read_btn = QtWidgets.QPushButton(self.centralwidget)
        self.save1_sound_btn = QtWidgets.QPushButton(self.centralwidget)
        self.read2_morse_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop2_read_btn = QtWidgets.QPushButton(self.centralwidget)
        self.save2_sound_btn = QtWidgets.QPushButton(self.centralwidget)
        self.field1 = QtWidgets.QTextEdit(self.centralwidget)
        self.field1.installEventFilter(self)
        self.field2 = QtWidgets.QTextEdit(self.centralwidget)
        self.field2.installEventFilter(self)
        self.change_lang_btn.installEventFilter(self)
        self.background.installEventFilter(self)
        self.read1_morse_btn.installEventFilter(self)
        self.read2_morse_btn.installEventFilter(self)
        self.stop1_read_btn.installEventFilter(self)
        self.stop2_read_btn.installEventFilter(self)
        self.save1_sound_btn.installEventFilter(self)
        self.save2_sound_btn.installEventFilter(self)
        self.field_temp = ""
        self.morse_string = ""
        self.check = ""
        self.engine = tts.init()
        self.Ttts = None
        self.menu_bar = QMenuBar()
        self.settings = None
        self.help = None
        self.about = None
        self.report = None

    def setup_ui(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.setEnabled(True)
        main_window.setFixedSize(600, 600)

        self.centralwidget.setObjectName("centralwidget")

        self.background.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.background.setStyleSheet("p")
        self.background.setText("")
        self.background.setPixmap(QtGui.QPixmap("resources/app_img/background.png"))
        self.background.setObjectName("background")
        self.background.setMouseTracking(True)

        self.menu_bar.setStyleSheet("background: url(resources/app_img/background.png);")
        self.menu_bar.addAction("Settings", lambda: self.show_settings())
        self.menu_bar.addAction("Help", lambda: self.show_help())
        self.menu_bar.addAction("About", lambda: self.show_about())
        self.menu_bar.addAction("Bug report", lambda: self.show_report())

        main_window.setMenuBar(self.menu_bar)

        self.font.setPointSize(25)
        self.font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.change_lang_btn.setGeometry(QtCore.QRect(210, 260, 200, 70))
        self.change_lang_btn.setFont(self.font)
        self.change_lang_btn.setStyleSheet(self.style_button)
        self.change_lang_btn.setFlat(False)
        self.change_lang_btn.setObjectName("change_lang")
        self.change_lang_btn.setText("Zamień")
        self.change_lang_btn.clicked[bool].connect(self.change_lang_func)

        self.font.setPointSize(20)

        self.field2.setGeometry(QtCore.QRect(60, 40, 490, 180))
        self.field2.setFont(self.font)
        self.field2.setStyleSheet(self.style_input)
        self.field2.setObjectName("field2")
        self.field2.setPlaceholderText("Wpisz tekst do przetłumaczenia")
        self.field2.verticalScrollBar().setStyleSheet(self.style_scroll_bar)
        self.field2.horizontalScrollBar().setEnabled(False)
        self.field2.setAcceptRichText(False)

        self.read1_morse_btn.setGeometry(QtCore.QRect(552, 64, 45, 45))
        self.read1_morse_btn.setStyleSheet(self.style_side_btn)
        self.read1_morse_btn.setIcon(QtGui.QIcon("resources\\app_img\\read_morse_btn.png"))
        self.read1_morse_btn.setIconSize(QtCore.QSize(25, 25))

        self.stop1_read_btn.setGeometry(QtCore.QRect(552, 111, 45, 45))
        self.stop1_read_btn.setStyleSheet(self.style_side_btn)
        self.stop1_read_btn.setIcon(QtGui.QIcon("resources\\app_img\\stop_read_btn.png"))
        self.stop1_read_btn.setIconSize(QtCore.QSize(25, 25))

        self.save1_sound_btn.setGeometry(QtCore.QRect(552, 158, 45, 45))
        self.save1_sound_btn.setStyleSheet(self.style_side_btn)
        self.save1_sound_btn.setIcon(QtGui.QIcon("resources\\app_img\\save_btn.png"))
        self.save1_sound_btn.setIconSize(QtCore.QSize(25, 25))

        self.field1.setGeometry(QtCore.QRect(60, 370, 490, 180))
        self.field1.setFont(self.font)
        self.field1.setStyleSheet(self.style_input)
        self.field1.setObjectName("field1")
        self.field1.setReadOnly(True)
        self.field1.verticalScrollBar().setStyleSheet(self.style_scroll_bar)
        self.field1.horizontalScrollBar().setEnabled(False)
        self.field1.setAcceptRichText(False)

        self.read2_morse_btn.setGeometry(QtCore.QRect(552, 395, 45, 45))
        self.read2_morse_btn.setStyleSheet(self.style_side_btn)
        self.read2_morse_btn.setIcon(QtGui.QIcon("resources\\app_img\\read_morse_btn.png"))
        self.read2_morse_btn.setIconSize(QtCore.QSize(25, 25))

        self.stop2_read_btn.setGeometry(QtCore.QRect(552, 442, 45, 45))
        self.stop2_read_btn.setStyleSheet(self.style_side_btn)
        self.stop2_read_btn.setIcon(QtGui.QIcon("resources\\app_img\\stop_read_btn.png"))
        self.stop2_read_btn.setIconSize(QtCore.QSize(25, 25))

        self.save2_sound_btn.setGeometry(QtCore.QRect(552, 489, 45, 45))
        self.save2_sound_btn.setStyleSheet(self.style_side_btn)
        self.save2_sound_btn.setIcon(QtGui.QIcon("resources\\app_img\\save_btn.png"))
        self.save2_sound_btn.setIconSize(QtCore.QSize(25, 25))

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def eventFilter(self, obj, event):
        if obj is self.field2:
            if event.type() == QEvent.Type.KeyRelease:
                self.polish_to_morse()
        elif obj is self.change_lang_btn:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.style_button = """
                        border: 2px solid grey;
                        border-radius: 20px;
                        color: black;
                        background-color: rgba(0, 0, 0, 0.13);
                        """

                self.change_lang_btn.setStyleSheet(self.style_button)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.style_button = """
                        border: 2px solid black;
                        border-radius: 20px;
                        color: black;
                        """

                self.change_lang_btn.setStyleSheet(self.style_button)
        elif obj is self.field1:
            if event.type() == QEvent.Type.KeyRelease:
                self.morse_to_polish()
        elif obj is self.read1_morse_btn:
            if event.type() == QEvent.Type.MouseButtonPress:
                if self.field2.toPlainText() != "":
                    data = self.field2.toPlainText()
                else:
                    data = self.field2.placeholderText()

                self.read_text(data)
        elif obj is self.read2_morse_btn:
            pass

            """
            if event.type() == QEvent.Type.MouseButtonPress:
                if self.field2.toPlainText() != "":
                    self.read_text(self.field1.toPlainText())
                else:
                    self.read_text(self.field1.placeholderText())"""
        elif obj is self.stop1_read_btn:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.stop_read()
        elif obj is self.stop2_read_btn:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.read_text(self.field1.toPlainText(), True)
        elif obj is self.save1_sound_btn:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.save_sound(self.field2.toPlainText())
        elif obj is self.save2_sound_btn:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.save_sound(self.field1.toPlainText())

        return super().eventFilter(obj, event)

    def show_settings(self):
        if self.settings is None:
            self.settings = Settings()

        self.settings.show()
        self.settings.activateWindow()

    def show_help(self):
        if self.help is None:
            self.help = Help()

        self.help.show()
        self.help.activateWindow()

    def show_about(self):
        if self.about is None:
            self.about = About()

        self.about.show()
        self.about.activateWindow()

    def show_report(self):
        if self.report is None:
            self.report = Report()

        self.report.show()
        self.report.activateWindow()

    def change_lang_func(self):
        if self.field2.placeholderText() != "":
            self.field2.setPlaceholderText("")
            self.field2.setReadOnly(True)

            self.field1.setReadOnly(False)
            self.field1.setPlaceholderText("Wpisz kod do przetłumaczenia")
        else:
            self.field2.setPlaceholderText("Wpisz tekst do przetłumaczenia")
            self.field2.setReadOnly(False)

            self.field1.setPlaceholderText("")
            self.field1.setReadOnly(True)

        self.field1.setText("")
        self.field2.setText("")

    def polish_to_morse(self):
        translation = ""
        self.field_value = self.field2.toPlainText().upper()

        for char in self.field_value:
            if char == " ":
                translation += " | "
            elif char not in self.chars_value.keys():
                translation = "Znaleziono nieznany znak"
                break
            elif char != " ":
                translation += self.chars_value[char] + " "

        self.field1.setText(translation)
        self.field1.verticalScrollBar().setValue(self.field1.verticalScrollBar().maximum())

    def morse_to_polish(self):
        translation = ""
        pattern = "^[.-]{1,7}$"
        words = self.field1.toPlainText().split(" | ")
        words_chars = []
        self.check = True
        self.field2.setText("")

        if self.field1.toPlainText() != "":
            for i in range(0, len(words)):
                words[i] = words[i].strip()
                words_chars.append(words[i].split(" "))

            for word in words_chars:
                if not self.check:
                    break
                else:
                    for char in word:
                        self.check = match(pattern, char)

                        if self.check and char in self.morse_value.keys():
                            translation += self.morse_value[char]
                        elif not self.check or char not in self.morse_value.keys():
                            translation = "Błędne kodowanie!"
                            break

                    translation += " "

            self.field2.setText(translation)
            self.field1.verticalScrollBar().setValue(self.field1.verticalScrollBar().maximum())

    def read_text(self, data, stop=False):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', voices[1].id)
        self.engine.say(data)
        self.engine.runAndWait()

    def stop_read(self):
        self.engine.endLoop()

    def save_sound(self, data):
        print("Saving...")


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowTitle("MorsePy")
    MainWindow.setWindowIcon(QtGui.QIcon("resources\\app_img\\icon.png"))
    ui = MorseApp()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    exit(app.exec())
