import kivy
kivy.require('1.0.6') # replace with your current kivy version !

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
import platform, os, stream2chromecast

devices = []
csystem = platform.system()

class StartCastButton(Widget):
	waiting_devices_popup = Popup(title = 'Choose a device', content=Label(text='Loading devices... Please wait'), auto_dismiss=False)

	def cancel_cast(self, instance):
		self.waiting_devices_popup.dismiss()

	def start_cast_on_device(self, chosenFile, device, instance):
		print (device)
		stream2chromecast.play(chosenFile, False, None, None, None, 0, device[0], None, None, None, None)

	def list_devices(self, chosenFile, instance):
		devices = stream2chromecast.list_devices()

		popup_content = GridLayout(cols=1)

		for device in devices:
			cast_device_button = Button(text = device[1])
			cast_device_button.bind(on_press = partial(self.start_cast_on_device, chosenFile, device))
			popup_content.add_widget(cast_device_button)

		cancel_button = Button(text = 'Cancel')
		cancel_button.bind(on_press = self.cancel_cast)

		popup_content.add_widget(cancel_button)

		self.waiting_devices_popup.content = popup_content

	def on_cast_start(self, chosenFile, instance):
		print (chosenFile)

		if chosenFile != '/':
			self.waiting_devices_popup.bind(on_open = partial(self.list_devices, chosenFile))
			self.waiting_devices_popup.open()
			print ('cast... cast... cast...')

		return True

class FileScreen(GridLayout):
	def __init__(self, **kwargs):
		super(FileScreen, self).__init__(**kwargs)

		cb = StartCastButton()

		self.cols = 1
		self.username = TextInput(multiline = False)
		
		self.file_button = Button(text = 'Choose a file...')
		self.file_button.bind(on_press=self.open_file_chooser)
		self.add_widget(self.file_button)

		self.cast_button = Button(text = 'Cannot cast yet. Choose a file first!')
		self.add_widget(self.cast_button)

		self.chosenFile = ''
		self.fileChooser = FileChooserListView(path='/', size_hint=(1, 5), dirselect=False)
		self.fileChooserPopup = fileChooserPopup = Popup(
			title = 'Choose a file', 
			content=Label(text='Loading files... Please wait'), 
			auto_dismiss=False
		)

		self.fileChooserPopupContent = GridLayout(cols=1)
		self.fileChooserPopupContent.add_widget(self.fileChooser)

		self.fileChooserChooseBtn = Button(text = 'Choose')
		self.fileChooserChooseBtn.bind(on_press = self.choose_file)

		self.fileChooserPopupContent.add_widget(self.fileChooserChooseBtn)
		self.fileChooserPopup.content = self.fileChooserPopupContent

	def choose_file(self, instance):
		cb = StartCastButton()

		if len(self.fileChooser.selection) > 0:
			self.chosenFile = self.fileChooser.selection[0]
			self.file_button.text = self.chosenFile
			self.cast_button.text = 'Cast now'
			self.cast_button.bind(on_press = partial(cb.on_cast_start, self.chosenFile))

		print (self.chosenFile)

		self.fileChooserPopup.dismiss()

	def open_file_chooser(self, instance):
		self.fileChooserPopup.open()

class MyApp(App):
		def build(self):
			return FileScreen()

if __name__ == '__main__':
		MyApp().run()