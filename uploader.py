import os.path as path

import requests
import wx


class AudioUploader(wx.Frame):
	"""Application to allow uploading of audio files to SndUp and other similar services"""
	def __init__(self, title):
		wx.Frame.__init__(self, None, title=title, size=(350,200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.select_file = wx.Button(self.panel, -1, "Select File")
		self.select_file.Bind(wx.EVT_BUTTON, self.SelectFile)
		self.main_box.Add(self.select_file, 0, wx.ALL, 10)
		self.link_label = wx.StaticText(self.panel, -1, "Audio URL")
		self.link = wx.TextCtrl(self.panel, -1, "",style=wx.TE_READONLY)
		self.main_box.Add(self.link, 0, wx.ALL, 10)
		self.upload = wx.Button(self.panel, -1, "Upload")
		self.upload.Bind(wx.EVT_BUTTON, self.StartUpload)
		self.main_box.Add(self.upload, 0, wx.ALL, 10)
		self.upload.Hide()
		self.close = wx.Button(self.panel, wx.ID_CLOSE, "Close")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()

	def StartUpload(self,event):
		"""Starts an upload; only runs after a standard operating system find file dialog has been shown and a file selected"""
		self.select_file.Disable()
		self.upload.Disable()
		#this is where things go weirdly
		r=requests.post("http://www.sndup.net/post.php", files={"file":open(self.filename,'rb')})
		self.link.ChangeValue(r.text)
		self.link.SetFocus()

	def SelectFile(self,event):
		"""Opens a standard OS find file dialog to find an audio file to upload"""
		openFileDialog = wx.FileDialog(self, "Select the audio file to be uploaded", "", "", "Audio Files (*.mp3, *.ogg, *.wav)|*.mp3; *.ogg; *.wav", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return False
		self.filename= openFileDialog.GetPath()
		self.name=path.basename(self.filename)
		self.upload.Show()

	def OnClose(self, event):
		"""App close event handler"""
		self.Destroy()


app = wx.App(redirect=False)
window=AudioUploader("Audio uploader")
window.Show()
app.MainLoop()