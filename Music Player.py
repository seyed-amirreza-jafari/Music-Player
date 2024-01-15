from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, \
QLabel, QPushButton, QSlider
from PyQt5.QtCore import QTimer
from PyQt5 import uic
from pygame import mixer
from mutagen.mp3 import MP3
import sys
import os
import csv

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi('Music_Player.ui', self)

        self.status_label = self.findChild(QLabel, 'status_label')
        self.track_label = self.findChild(QLabel, 'track_label')
        self.musics_list = self.findChild(QListWidget, 'musics_list')
        self.pause_button = self.findChild(QPushButton, 'pause_button')
        self.next_button = self.findChild(QPushButton, 'next_button')
        self.previous_button = self.findChild(QPushButton, 'previous_button')
        self.play_button = self.findChild(QPushButton, 'play_button')
        self.remove_button = self.findChild(QPushButton, 'remove_button')
        self.upload_button = self.findChild(QPushButton, 'upload_button')
        self.clear_list_button = self.findChild(QPushButton, 'clear_list_button')
        self.time_slider = self.findChild(QSlider, 'time_slider')
        self.time_label = self.findChild(QLabel, 'time_label')
        self.timer_label = self.findChild(QLabel, 'timer_label')
        self.volume_slider = self.findChild(QSlider, 'volume_slider')
        self.volume_label = self.findChild(QLabel, 'volume_label')

        self.status_label.setText('Status: None')

        with open('Musics.csv') as csvFile:
            data = csvFile.readlines()

            if data:
                for row in data:
                    name = row.split(',')[0]
                    self.musics_list.addItem(name)

        self.time_slider.setEnabled(False)
        self.volume_slider.setEnabled(False)
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.remove_button.setEnabled(False)

        self.musics_list.itemSelectionChanged.connect(self.rowChanged)

        self.all_musics_action.triggered.connect(self.open_allMusics_txt)

        self.timer = QTimer(self)
        self.start = False
        self.counter = 0

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

        self.clear_list_button.clicked.connect(self.clear)
        self.volume_slider.valueChanged.connect(self.set_vol)
        self.play_button.clicked.connect(self.play)
        self.timer.timeout.connect(self.showTime)
        self.pause_button.clicked.connect(self.pause)
        try:
            self.next_button.clicked.connect(self.next)
        except: pass
        try:
            self.previous_button.clicked.connect(self.previous)
        except: pass
        self.upload_button.clicked.connect(self.upload)
        self.remove_button.clicked.connect(self.remove)

        self.timer.start(1000)

        self.show()

    def rowChanged(self):
        try:
            self.track_label.setText(f'Track: {self.musics_list.currentItem().text()}')

            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.remove_button.setEnabled(True)

        except: pass

    def open_allMusics_txt(self):
        path = os.getcwd() + '/Musics.csv'

        os.startfile(path)

    def play(self):
        self.timer_label.setText('00:00')
        self.status_label.setText('Status: Playing')

        self.time_slider.setValue(0)
        self.volume_slider.setEnabled(True)

        with open('Musics.csv') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                name = row[0]
                if name == self.musics_list.currentItem().text():
                    self.length = row[2]
                    break

            self.time_slider.setMaximum(int(self.length))

        with open('Musics.csv') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                name = row[0]
                if name == self.musics_list.currentItem().text():
                    path = row[1]
                    break

        mixer.init()

        mixer.music.load(path)
        mixer.music.set_volume(0.5)
        mixer.music.play()

        self.counter = int(self.length)

        length = int(self.length)

        self.time_slider.setMaximum(length)
        self.volume_slider.setValue(int(mixer.music.get_volume() * 100))

        mins = length // 60
        length %= 60

        seconds = length

        if len(str(mins)) == 1 and len(str(seconds)) == 1:
            self.time_label.setText(f'0{mins}:0{seconds}')
        elif len(str(mins)) == 1:
            self.time_label.setText(f'0{mins}:{seconds}')
        elif len(str(seconds)) == 1:
            self.time_label.setText(f'{mins}:0{seconds}')
        else:
            self.time_label.setText(f'{mins}:{seconds}')

        self.start = True
        if self.counter == 0:
            self.start = False

    def showTime(self):
        if self.start:
            self.counter -= 1
            if self.counter == 0:
                self.start = False
                self.timer_label.setText("00:00")
                self.time_slider.setValue(0)
                self.time_slider.setEnabled(False)
        if self.start:
            tempCounter = int(self.length) - self.counter
            self.time_slider.setValue(tempCounter)

            mins = tempCounter // 60
            seconds = tempCounter % 60

            if len(str(mins)) == 1 and len(str(seconds)) == 1:
                self.timer_label.setText(f'0{mins}:0{seconds}')
            elif len(str(mins)) == 1:
                self.timer_label.setText(f'0{mins}:{seconds}')
            elif len(str(seconds)) == 1:
                self.timer_label.setText(f'{mins}:0{seconds}')
            else:
                self.timer_label.setText(f'{mins}:{seconds}')

    def pause(self):
        self.status_label.setText('Status: Pause')

        self.time_slider.setEnabled(False)
        self.volume_slider.setEnabled(False)

        with open('Musics.csv') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                name = row[0]
                if name == self.musics_list.currentItem().text():
                    path = row[1]
                    break

        mixer.init()

        mixer.music.load(path)
        mixer.music.pause()

        self.start = False

    def next(self):
        self.musics_list.setCurrentRow(self.musics_list.currentRow()+1)

    def previous(self):
        self.musics_list.setCurrentRow(self.musics_list.currentRow()-1)

    def remove(self):
        listItems = self.musics_list.selectedItems()
        if not listItems: return    
        for item in listItems:
            self.musics_list.takeItem(self.musics_list.row(item))

        self.track_label.setText('Track:')

        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.remove_button.setEnabled(False)

    def clear(self):
        self.musics_list.clear()
        with open('Musics.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)

            writer.writerows('')

        self.track_label.setText('Track:')

        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.remove_button.setEnabled(False)

    def set_vol(self):
        mixer.music.set_volume(self.volume_slider.value()/100)
        self.volume_label.setText(str(self.volume_slider.value()))

    def upload(self):
        try:
            music = QFileDialog.getOpenFileName(self, 'open file', \
            'C:/Users/user/Desktop/Musics', 'All Files (*);;Musics (*.mp3)')

            self.music_path = music[0]

            self.music_name = self.music_path.split('/')[-1]
            self.music_length = int(MP3(self.music_path).info.length)

            information = [self.music_name, self.music_path, self.music_length]

            flag = 0

            listItems = [self.musics_list.item(i).text() for i in range(self.musics_list.count())]

            for item in listItems:
                if item == self.music_name:
                    flag = 1

            if flag == 0:
                self.musics_list.addItem(self.music_name)
                with open('Musics.csv', 'a', newline = '') as csvFile:
                    writer = csv.writer(csvFile)

                    writer.writerow(information)
        except: pass

app = QApplication(sys.argv)
Window = UI()
app.exec_()