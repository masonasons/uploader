import tweepy
import webbrowser
import config_utils
import os.path as path
import sys
import urllib

import requests
import wx

# Globals

tw1="MneWylqkykEp95neIxCvN1i2J" # twitter app key
tw2="jPdug6Dl9IWxJvtsaQRqT120jYKf8bXl3drKFshw8JzGQCm6XX" # twitter app secret
services = ['SNDUp', 'TWUp', 'SoundCache'] # supported audio upload services


class AudioUploader(wx.Frame):
	"""Application to allow uploading of audio files to SndUp and other similar services"""
	def __init__(self, title):
		wx.Frame.__init__(self, None, title=title, size=(350,200)) # initialize the wx frame
		# load config and validate a specification file
		self.MAINFILE = "uploader.cfg"
		self.MAINSPEC = "app.defaults"
		self.appconfig = config_utils.load_config(self.MAINFILE, self.MAINSPEC)
		# window events and controls
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.select_file = wx.Button(self.panel, -1, "&Select File")
		self.select_file.Bind(wx.EVT_BUTTON, self.SelectFile)
		self.main_box.Add(self.select_file, 0, wx.ALL, 10)
		self.link_label = wx.StaticText(self.panel, -1, "Audio UR&L")
		self.link = wx.TextCtrl(self.panel, -1, "",style=wx.TE_READONLY)
		self.main_box.Add(self.link, 0, wx.ALL, 10)
		self.key_label = wx.StaticText(self.panel, -1,"SNDUp API &Key")
		self.key = wx.TextCtrl(self.panel, -1, "")
		self.main_box.Add(self.key, 0, wx.ALL, 10)
		self.key.SetValue(self.appconfig["general"]["APIKey"])
		self.services_label=wx.StaticText(self.panel, -1, "Upload to")
		self.services = wx.ComboBox(self.panel, -1, choices=services, value=services[0], style=wx.CB_READONLY)
		self.services.Bind(wx.EVT_COMBOBOX, self.on_service_change)
		self.main_box.Add(self.services, 0, wx.ALL, 10)
		self.upload = wx.Button(self.panel, -1, "&Upload")
		self.upload.Bind(wx.EVT_BUTTON, self.StartUpload)
		self.main_box.Add(self.upload, 0, wx.ALL, 10)
		self.upload.Hide()
		self.twitter_label = wx.StaticText(self.panel, -1,"Tweet Te&xt")
		self.twitter_text = wx.TextCtrl(self.panel, -1, "")
		self.main_box.Add(self.twitter_text, 0, wx.ALL, 10)
		self.twitter_text.Hide()
		self.tweet = wx.Button(self.panel, -1, "&Tweet")
		self.tweet.Bind(wx.EVT_BUTTON, self.Tweet)
		self.tweet.Hide()
		self.main_box.Add(self.tweet, 0, wx.ALL, 10)
		self.new = wx.Button(self.panel, -1, "&Attach another file")
		self.new.Bind(wx.EVT_BUTTON, self.Reset)
		self.main_box.Add(self.new, 0, wx.ALL, 10)
		self.new.Hide()
		self.close = wx.Button(self.panel, wx.ID_CLOSE, "&Close")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()

	def StartUpload(self,event):
		"""Starts an upload; only runs after a standard operating system find file dialog has been shown and a file selected"""
		self.services.Hide()
		self.select_file.Hide()
		self.upload.Hide()
		self.key.Hide()
		self.twitter_text.Show()
		self.tweet.Show()

		if self.services.GetValue()=="SNDUp":
			if self.key.GetValue() != "":
				r=requests.post("http://www.sndup.net/post.php", files={"file":open(self.filename,'rb')}, data={'api_key':self.key.GetValue()})
			else:
				r=requests.post("http://www.sndup.net/post.php", files={"file":open(self.filename,'rb')})
		elif self.services.GetValue()== "TWUp":
			r=requests.post("http://api.twup.me/post.json", files={"file":open(self.filename,'rb')})
		elif self.services.GetValue() == "SoundCache":
			r = requests.post("http://soundcache.tk/upload.php", files={"file":open(self.filename,'rb')})
		self.link.ChangeValue(handle_URL(r.json()))
		self.link.SetFocus()
		self.new.Show()

	def SelectFile(self,event):
		"""Opens a standard OS find file dialog to find an audio file to upload"""
		openFileDialog = wx.FileDialog(self, "Select the audio file to be uploaded", "", "", "Audio Files (*.mp3, *.ogg, *.wav)|*.mp3; *.ogg; *.wav", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return False
		self.filename= openFileDialog.GetPath()
		self.name=path.basename(self.filename)
		self.upload.Show()

	def Tweet(self, event):
		auth = tweepy.OAuthHandler(tw1, tw2)
		if self.appconfig["general"]["TWKey"]=="" or self.appconfig["general"]["TWSecret"]=="":
			webbrowser.open(auth.get_authorization_url())
			verifier = ask(parent=self, message='Enter pin:')
			auth.get_access_token(verifier)
			self.appconfig["general"]["TWKey"]=auth.access_token
			self.appconfig["general"]["TWSecret"]=auth.access_token_secret
			self.appconfig.write()
		else:
			auth.set_access_token(self.appconfig["general"]["TWKey"], self.appconfig["general"]["TWSecret"])
		api = tweepy.API(auth)
		api.update_status(self.twitter_text.GetValue()+" "+self.link.GetValue()+" #audio")

	def Reset(self, event):
		self.twitter_text.SetValue("")
		self.twitter_text.Hide()
		self.tweet.Hide()
		self.services.Show()
		self.upload.Hide()
		self.new.Hide()
		self.select_file.Show()
		self.key.Show()
		self.select_file.SetFocus()
		self.link.ChangeValue("")

	def on_service_change(self, event):
		"""Event handler for when the service combo box changes.
			Currently it just hides unnecessary fields for different services. For example, TWUp doesn't have an API key system, so we shouldn't keep the text field that SNDUp needs when it isn't selected.
		"""
		dir(event)
		if event.GetString() == 'SNDUp':
			self.key.Show()
		else:
			self.key.Hide()

	def OnClose(self, event):
		"""App close event handler"""
		self.appconfig["general"]["APIKey"]=self.key.GetValue()
		self.appconfig.write()
		self.Destroy()

def handle_URL(url):
	"""Properly converts an escaped URL to a proper one, taking into account the difference in python 2 and python 3"""
	# We are passed a python dict by default, as SndUp's response is json and we convert that to a dict with .json()
	# So extract the URL from the dict:
	url = url['url']
	if sys.version_info[0]==2: # running python 2
		final_url = urllib.unquote(url)
	elif sys.version_info[1]==3:
		final_url = urllib.parse.unquote(url)
	return final_url

def ask(parent=None, message='', default_value=''):
	"""Simple dialog to get a response from the user"""
	dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
	dlg.ShowModal()
	result = dlg.GetValue()
	dlg.Destroy()
	return result


app = wx.App(redirect=False)
window=AudioUploader("Audio uploader")
window.Show()
app.MainLoop()