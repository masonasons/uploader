import config_utils
import os.path as path
import sys
import urllib

import requests
import wx

MAINFILE = "uploader.cfg"
MAINSPEC = "app.defaults"
appconfig = config_utils.load_config(MAINFILE,MAINSPEC)
class AudioUploader(wx.Frame):
	"""Application to allow uploading of audio files to SndUp and other similar services"""
	def __init__(self, title):
		wx.Frame.__init__(self, None, title=title, size=(350,200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.select_file = wx.Button(self.panel, -1, "&Select File")
		self.select_file.Bind(wx.EVT_BUTTON, self.SelectFile)
		self.main_box.Add(self.select_file, 0, wx.ALL, 10)
		self.link_label = wx.StaticText(self.panel, -1, "Audio UR&L")
		self.link = wx.TextCtrl(self.panel, -1, "",style=wx.TE_READONLY)
		self.main_box.Add(self.link, 0, wx.ALL, 10)
		self.key_label = wx.StaticText(self.panel, -1,"API &Key")
		self.key = wx.TextCtrl(self.panel, -1, "")
		self.main_box.Add(self.key, 0, wx.ALL, 10)
		self.key.SetValue(appconfig["general"]["APIKey"])

		self.upload = wx.Button(self.panel, -1, "&Upload")
		self.upload.Bind(wx.EVT_BUTTON, self.StartUpload)
		self.main_box.Add(self.upload, 0, wx.ALL, 10)
		self.upload.Hide()
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
		self.select_file.Hide()
		self.upload.Hide()
		self.key.Hide()
		r=requests.post("http://www.sndup.net/post.php", files={"file":open(self.filename,'rb')}, data={'api_key':self.key.GetValue()})
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

	def Reset(self, event):
		self.upload.Hide()
		self.new.Hide()
		self.select_file.Show()
		self.key.Show()
		self.select_file.SetFocus()
		self.link.ChangeValue("")

	def OnClose(self, event):
		"""App close event handler"""
		appconfig["general"]["APIKey"]=self.key.GetValue()
		appconfig.write()

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

app = wx.App(redirect=False)
window=AudioUploader("Audio uploader")
window.Show()
app.MainLoop()