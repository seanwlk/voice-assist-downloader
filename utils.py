import requests
import urllib

def convert_bytes(n):
  n = int(n)
  stepUnit = 1024
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    if n < stepUnit:
      return "%3.1f %s" % (n, x)
    n /= stepUnit

class IFTTTNotifications:
  def __init__(self, applet, key, enabled):
    self.key = key
    self.applet = applet
    self.enabled = enabled
  def notify(self,data):
    if self.enabled:
      if data['status'] == "success":
        title = "Download started"
      else:
        title = "Download failed"
      message = data['message']
      if 'image' in data:
        image = data['image']
      else:
        image = ""
      requests.post(f"https://maker.ifttt.com/trigger/{self.applet}/with/key/{self.key}?value1={title}&value2={message}&value3={image}")
