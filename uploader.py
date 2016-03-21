import os.path as path
import requests
import wx

#probably a more efficient way to do this, but oh well.

class Frame(wx.Frame):
	def __init__(self, title):
		wx.Frame.__init__(self, None, title=title, size=(350,200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		panel = wx.Panel(self)
		box = wx.BoxSizer(wx.VERTICAL)
		self.m_add = wx.Button(panel, -1, "Select File")
		self.m_add.Bind(wx.EVT_BUTTON, self.SelectFile)
		box.Add(self.m_add, 0, wx.ALL, 10)
		self.m_link_label = wx.StaticText(panel, -1, "Link")
		self.m_link = wx.TextCtrl(panel, -1, "",style=wx.TE_READONLY)
		box.Add(self.m_link, 0, wx.ALL, 10)
		self.m_upload = wx.Button(panel, -1, "Upload")
		self.m_upload.Bind(wx.EVT_BUTTON, self.StartUpload)
		box.Add(self.m_upload, 0, wx.ALL, 10)
		self.m_upload.Hide()
		self.m_close = wx.Button(panel, wx.ID_CLOSE, "Cancel")
		self.m_close.Bind(wx.EVT_BUTTON, self.OnClose)
		box.Add(self.m_close, 0, wx.ALL, 10)
		panel.Layout()
	def StartUpload(self,event):
		self.m_add.Disable()
		self.m_upload.Disable()
#this is where things go weirdly
		r=requests.post("http://www.sndup.net/post.php",{"file":open(self.filename,'rb')})
#temporary, won't parse yet until I know it works
		self.m_link.ChangeValue(r.text)
		self.m_link.SetFocus()

	def SelectFile(self,event):
		openFileDialog = wx.FileDialog(self, "Select the audio file to be uploaded", "", "", "Audio Files (*.mp3, *.ogg, *.wav)|*.mp3; *.ogg; *.wav", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return False
		self.filename= openFileDialog.GetPath()
		self.name=path.basename(self.filename)
		self.m_upload.Show()
	def OnClose(self, event):
		self.Destroy()
app = wx.App(redirect=False)
window=Frame("Audio uploader")
window.Show()
app.MainLoop()