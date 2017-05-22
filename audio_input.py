import paths
import platform
import subprocess
import os
import tempfile
import sound_lib
from sound_lib import input
from sound_lib import recording

class AudioInput(object):
	def __init__(self):
		self.is_recording=False
		self.input = input.Input()
		self.recordingname=""
		self.filename=""
		self.name=""

	def encode(self,filename, quality=4.5):
		system = platform.system()
		if system == "Windows":
			subprocess.call(r'"%s" -q %r "%s"' % (paths.app_path('oggenc2.exe'), quality, filename))
			return self.filename.replace(".wav",".ogg")
		else:
			print "Converting not implimented for this operating system. WAV file incoming."
			return self.filename

	def start_recording(self):
		self.filename = tempfile.mktemp(suffix='.wav')
		self.recording = self.recording(self.filename)
		self.recording.play()

	def stop_recording(self):
		self.recording.stop()
		self.recording.free()
		self.recordname=self.filename
		self.filename=self.encode(self.filename)


#Internal Functions
	def cleanup(self):
		os.remove(self.filename)
		os.remove(self.recordname)
		self.is_recording=False

	def recording(self,filename):
		val = recording.WaveRecording(filename=filename)
		return val