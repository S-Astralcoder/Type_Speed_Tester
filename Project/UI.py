from html import escape

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, \
    QPushButton, QTextEdit, QSizePolicy

from PySide6.QtCore import Qt, QTimer, Slot
import random
from text_database import Sentence

class UI_MainWindow(QMainWindow):
    def __init__(self):
        self._max_timer = 60
        self._conf_timer = self._max_timer / 60

        self._timer_count = 0
        self._actual_total = 0
        self._total_words = 0
        self._correct_words = 0
        self._previous_index = 0


        self._sentence_selected = None
        self._broken_sentence = None

        super().__init__()
        self.setWindowTitle("Type Speed Tester")
        self.resize(1000, 800)

        container = QWidget()
        container.setObjectName("main_container")
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(20)

        # title section
        self.title_header = QFrame()
        self.title_header.setObjectName("title_header")
        self.title_header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title_header_layout = QVBoxLayout(self.title_header)
        self.title_header_layout.setContentsMargins(20, 18, 20, 18)
        self.title_header_layout.setSpacing(6)

        self.title_label = QLabel("Type Speed Tester")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label = QLabel("Focus. Type clean. Beat your pace.")
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_header_layout.addWidget(self.title_label)
        self.title_header_layout.addWidget(self.subtitle_label)


        # status display section
        self.status_header = QFrame()
        self.status_header.setObjectName("status_header")
        self.status_header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.status_header_layout = QHBoxLayout(self.status_header)
        self.status_header_layout.setContentsMargins(16, 12, 16, 12)
        self.status_header_layout.setSpacing(12)

        # status widgets
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)


        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timer_label")
        self.wpm_label = QLabel("00 WPM")
        self.wpm_label.setObjectName("wpm_label")
        self.accuracy_label = QLabel("UK% ACC")
        self.accuracy_label.setObjectName("accuracy_label")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wpm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.wpm_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.accuracy_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.status_header_layout.addWidget(self.timer_label, 1)
        self.status_header_layout.addWidget(self.wpm_label, 1)
        self.status_header_layout.addWidget(self.accuracy_label, 1)


        # text progress display
        self.text_display = QFrame()
        self.text_display.setObjectName("text_display")
        self.text_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.text_display_layout = QVBoxLayout(self.text_display)
        self.text_display_layout.setContentsMargins(24, 24, 24, 24)
        self.text_display_layout.setSpacing(12)
        self.show_text = QTextEdit()
        self.show_text.setObjectName("show_text")
        self.show_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show_text.setPlaceholderText("Press start to test your speed.")
        self.track_text = QTextEdit()
        self.track_text.setObjectName("track_text")
        self.track_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.track_text.setPlaceholderText("Your progress will appear here.")

        self.show_text.setReadOnly(True)
        self.track_text.setReadOnly(True)

        self.text_display_layout.addWidget(self.show_text)
        self.text_display_layout.addWidget(self.track_text)


        self.input_text = QFrame()
        self.input_text.setObjectName("input_text")
        self.input_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.input_text_layout = QHBoxLayout(self.input_text)
        self.input_text_layout.setContentsMargins(16, 16, 16, 16)

        self.input_text_box = QTextEdit()
        self.input_text_box.setObjectName("input_text_box")
        self.input_text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.input_text_box.setPlaceholderText("Time will start the automatically when you start typing.")

        self.input_text_layout.addWidget(self.input_text_box)
        self.input_text_box.setEnabled(False)
        self.input_text_box.textChanged.connect(self._check_input)

        self.reset_button = QPushButton("Start")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_test)




        # layouts
        self.layout.addWidget(self.title_header)
        self.layout.addWidget(self.status_header)
        self.layout.addWidget(self.text_display)
        self.layout.addWidget(self.input_text)
        self.layout.addWidget(self.reset_button)
        self.setCentralWidget(container)

    def config(self, max_timer=None):
        if max_timer is not None:
            if max_timer <= 0:
                raise ValueError("max_timer must be greater than 0")
            self._max_timer = max_timer
            self._conf_timer = self._max_timer / 60

    def _time_up(self):
        self.input_text_box.setEnabled(False)
        self.reset_button.setEnabled(True)
        self.timer.stop()
        self._timer_count = 0
        self.wpm_label.setText(f"{int((self._actual_total // 5) // self._conf_timer)} WPM")
        accuracy = (self._correct_words / self._total_words) * 100 if self._total_words else 0
        self.accuracy_label.setText(f"{accuracy:.1f}% ACC")
        self.input_text_box.blockSignals(True)
        self.input_text_box.clear()
        self.input_text_box.blockSignals(False)

    @Slot()
    def _update_timer(self):
        if self._timer_count > self._max_timer:
            self._time_up()
            return
        self.timer_label.setText(f"{self._timer_count//60:02d}:{self._timer_count%60:02d}")
        self._timer_count += 1

    def _split_sentence(self):
        self._broken_sentence = list(self._sentence_selected)

    def reset_test(self):
        if self.reset_button.text() != "Reset":
            self.reset_button.setText("Reset")
        self.timer.stop()
        self._timer_count = 0
        self.input_text_box.blockSignals(True)
        self.input_text_box.clear()
        self.input_text_box.blockSignals(False)
        self.timer_label.setText("00:00")
        self.wpm_label.setText("00 WPM")
        self.accuracy_label.setText("UK% ACC")
        self._sentence_selected = random.choice(Sentence)
        self._split_sentence()
        self.show_text.setText(self._sentence_selected)
        self.track_text.setText(self._sentence_selected)
        self.show_text.setReadOnly(True)
        self.track_text.setReadOnly(True)
        self.reset_button.setEnabled(True)
        self.input_text_box.setEnabled(True)

        self._total_words = 0
        self._correct_words = 0
        self._actual_total = 0
        self._previous_index = 0

    def _check_input(self):
        if not self._sentence_selected or not self._broken_sentence:
            return

        if not self.timer.isActive():
            self.timer.start(1000)
        text_input = self.input_text_box.toPlainText()
        length = len(text_input)
        if length > len(self._sentence_selected):
            valid_input = text_input[:len(self._sentence_selected)]
            self._total_words = len(self._sentence_selected)
            self._correct_words = sum(
                text_input_char == sentence_char
                for text_input_char, sentence_char in zip(valid_input, self._sentence_selected)
            )
            self._actual_total = len(self._sentence_selected)
            self._time_up()
            return

        typed_sentence = self._sentence_selected[:length]
        remaining_sentence = self._sentence_selected[length:]
        highlighted_text = []
        correct_count = 0

        for text_input_char, sentence_char in zip(text_input, typed_sentence):
            if text_input_char == sentence_char:
                highlighted_text.append(f"<font color='green'>{escape(sentence_char)}</font>")
                correct_count += 1
            else:
                highlighted_text.append(f"<font color='red'>{escape(sentence_char)}</font>")

        highlighted_text.append(escape(remaining_sentence))

        self._previous_index = max(0, length - 1)
        self._total_words = length
        self._correct_words = correct_count
        self._actual_total = length
        self._broken_sentence = list(self._sentence_selected)
        self.track_text.setHtml("".join(highlighted_text))
