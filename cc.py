import kivy

kivy.require('1.0.6') # replace with your current kivy version !

import platform, os, stream2chromecast, atexit, sys, os.path

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from os.path import sep, expanduser, isdir, dirname
from functools import partial
from threading import Thread
from multiprocessing import Process
from collections import namedtuple
from kivy.config import Config

Config.set('kivy', 'exit_on_escape', '0')

devices = []
cdevice = ''
csystem = platform.system()

def exit_handler():
	print ('EXIT')

atexit.register(exit_handler)

#
# Start Cast (button)
#
class StartCastButton(Widget):
	def get_waiting_devices_popup(self):
		return Popup(title = 'Choose a device', content=Label(text='Searching for devices, please wait...'), auto_dismiss=False)

	def get_casting_popup(self):
		return Popup(title = 'Cast', content=Label(text='Casting...'), auto_dismiss=False)

	def cancel_cast(self, instance):
		self.waiting_devices_popup.dismiss()

	def play_cast(self, chosenFile, device):
		stream2chromecast.play(chosenFile, False, None, None, None, 0, device[0], None, None, None, None)

	def stop_cast_on_device(self, device, instance):
		stream2chromecast.stop(device[0])
		#sys.exit()
		self.cthread.terminate()
		self.casting_popup.dismiss()
		self.waiting_devices_popup.dismiss()

	def unpause_cast_on_device(self, device, instance):
		stream2chromecast.unpause(device[0])

	def pause_cast_on_device(self, device, instance):
		stream2chromecast.pause(device[0])

	def volume_up_on_device(self, device, instance):
		stream2chromecast.volume_up(device[0])

	def volume_down_on_device(self, device, instance):
		stream2chromecast.volume_down(device[0])

	def play_cast_on_device(self, chosenFile, device, instance):
		self.cthread = cthread = Process(target=self.play_cast, args=(chosenFile, device,))
		self.cthread.start()

	def start_cast_on_device(self, chosenFile, device, instance):
		cdevice = device[0]

		print (device)
		
		self.casting_popup_content = GridLayout(cols=1)
		self.casting_popup_content.add_widget(Label(text='Casting...'))
		self.casting_popup_content.add_widget(Label(text=chosenFile, text_size=(400, None), halign='center'))

		# Volume buttons
		self.casting_popup_volume_buttons = GridLayout(cols=2)

		self.casting_popup_volumedown_button = Button(text = 'Volume down', background_color=[2,1,2,1])
		self.casting_popup_volumedown_button.bind(on_press=partial(self.volume_down_on_device, device))
		self.casting_popup_volume_buttons.add_widget(self.casting_popup_volumedown_button)

		self.casting_popup_volumeup_button = Button(text = 'Volume up', background_color=[2,1,2,1])
		self.casting_popup_volumeup_button.bind(on_press=partial(self.volume_up_on_device, device))
		self.casting_popup_volume_buttons.add_widget(self.casting_popup_volumeup_button)

		self.casting_popup_content.add_widget(self.casting_popup_volume_buttons)

		# Playback control buttons
		self.casting_popup_playback_buttons = GridLayout(cols=3)
		
		self.casting_popup_pause_button = Button(text = 'Pause', background_color=[0,1,2,1])
		self.casting_popup_pause_button.bind(on_press=partial(self.pause_cast_on_device, device))
		self.casting_popup_playback_buttons.add_widget(self.casting_popup_pause_button)
		
		self.casting_popup_continue_button = Button(text = 'Continue', background_color=[0,1,2,1])
		self.casting_popup_continue_button.bind(on_press=partial(self.unpause_cast_on_device, device))
		self.casting_popup_playback_buttons.add_widget(self.casting_popup_continue_button)

		self.casting_popup_stop_button = Button(text = 'Stop', background_color=[3,0,2,1])
		self.casting_popup_stop_button.bind(on_press=partial(self.stop_cast_on_device, device))
		self.casting_popup_playback_buttons.add_widget(self.casting_popup_stop_button)

		self.casting_popup_content.add_widget(self.casting_popup_playback_buttons)

		# Play
		self.casting_popup = self.get_casting_popup()
		self.casting_popup.content = self.casting_popup_content
		self.casting_popup.bind(on_open = partial(self.play_cast_on_device, chosenFile, device))
		self.casting_popup.open()

	def list_devices(self, chosenFile, instance):
		devices = stream2chromecast.list_devices()

		popup_content = GridLayout(cols=1)

		for device in devices:
			cast_device_button = Button(text = device[1] + ' (' + device[0] + ')', background_color=[0,1,2,1])
			cast_device_button.bind(on_press = partial(self.start_cast_on_device, chosenFile, device))
			popup_content.add_widget(cast_device_button)

		cancel_button = Button(text = 'Cancel', background_color=[3,0,2,1])
		cancel_button.bind(on_press = self.cancel_cast)

		popup_content.add_widget(cancel_button)

		self.waiting_devices_popup.content = popup_content

	def on_cast_start(self, chosenFile, instance):
		print (chosenFile)

		if chosenFile != '/':
			self.waiting_devices_popup = self.get_waiting_devices_popup()
			self.waiting_devices_popup.bind(on_open = partial(self.list_devices, chosenFile))
			self.waiting_devices_popup.content = Label(text='Searching for devices, please wait...')
			self.waiting_devices_popup.open()
		
		return True

#
# Start Screen
#
class FileScreen(GridLayout):
	def __init__(self, **kwargs):
		super(FileScreen, self).__init__(**kwargs)

		cb = StartCastButton()

		self.cols = 1
		self.username = TextInput(multiline = False)

		self.logo_text = Label(text='Stream2chromecast GUI', font_size = '30sp')
		self.add_widget(self.logo_text)

		self.file_button = Button(text = 'Choose a file...', background_color=[0,1,2,1], text_size=(400, None), halign='center')
		self.file_button.bind(on_press=self.open_file_chooser)
		self.add_widget(self.file_button)

		self.cast_button = Button(text = 'Cannot cast yet. Choose a file first!', background_color=[3,0,2,1])
		self.add_widget(self.cast_button)

		self.chosenFile = ''
		self.fileChooser = FileChooserListView(path='/home', size_hint=(1, 5), dirselect=False)
		self.fileChooserPopup = fileChooserPopup = Popup(
			title = 'Choose a file', 
			content=Label(text='Loading files... Please wait'), 
			auto_dismiss=False
		)

		self.fileChooserPopupContent = GridLayout(cols=1)
		self.fileChooserPopupContent.add_widget(self.fileChooser)

		self.fileChooserChooseBtn = Button(text = 'Choose', background_color = [0,2,0,1])
		self.fileChooserChooseBtn.bind(on_press = self.choose_file)

		self.fileChooserPopupContent.add_widget(self.fileChooserChooseBtn)
		self.fileChooserPopup.content = self.fileChooserPopupContent

	def choose_file(self, instance):
		cb = StartCastButton()

		if len(self.fileChooser.selection) > 0 and os.path.isfile(self.fileChooser.selection[0]):
			self.chosenFile = self.fileChooser.selection[0]
			self.file_button.text = self.chosenFile
			self.cast_button.text = 'Cast now'
			self.cast_button.background_color = [0,2,0,1]
			self.cast_button.bind(on_press = partial(cb.on_cast_start, self.chosenFile))

		print (self.chosenFile)

		self.fileChooserPopup.dismiss()

	def open_file_chooser(self, instance):
		self.fileChooserPopup.open()

#
# App
#
class MyApp(App):
	title = 'Stream2chromecast GUI'

	def build(self):
		return FileScreen()

if __name__ == '__main__':
	MyApp().run()