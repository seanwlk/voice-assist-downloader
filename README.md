# Voice Assistant Downloader

Script for amateur bingers that allows you to request your Google Assistant (for now only that because I'm not sure if Siri or alexa have such integration with IFTTT) to download movies or the latest tv series episodes just with a voice command.
"Hey Google, download last week tonight" will for instance download the latest episode that aired in a specified lifespan in the config file.

#### Usage example

I've been using this for a year already to download stuff on my PLEX server at home. The current implementation runs on a Raspberry Pi which is exposed to the internet and then through RPC adds torrents thanks tho the application to my dedicated PLEX server. You could do this with a NAS from what I've seen. (I actually wanted to buy one and did some research, looks like both python, plex and even transmission can be installed on Qnap or Synology).
As said in the introduction, this at the moment is a POC with Google Assisntant but you could add support to Amazon Alexa i believe since it's on IFTTT (I don't own one so i can't test). At the current time I believe you can't with Siri but anyone can prove me wrong (please do).

## Requirements
- IFTTT account
- [OMDb API key](http://www.omdbapi.com/apikey.aspx)
- Python >= 3.6
- transmission-cli / web (on a VPS/Raspberry/QNAP/Synology/ Generic nas with support)
- transmissionrpc python library
- Flask
- Knowledge on how to open and forward ports
- Time

## Configuration
First you have to create an [IFTTT account](https://ifttt.com/) if you dont ha ve it already. Once logged in, do the following:
- Create a [new Applet](https://ifttt.com/create)
- Click on the "Plus" of the "If this" part
- Search for "Google Assistant" and click on it
- Connect to the Google account
- Select "Say a phrase with a text ingredient" as trigger
- Configure as follows ![Listener1](https://raw.githubusercontent.com/seanwlk/voice-assist-downloader/master/docs/images/listener1.jpg)
- You can also compile the other fields or change the keyword as you wish
- Click "Create Trigger" and then on the next screen click on the "Plus" of the "Then That" part
- Search for "Webhooks" and select it "Make web request"
- Here you will have to put your exposed address to the internet so that IFTTT can reach the endpoint and obviously you have to put the route name of the application, for example in the config Template there is `getOnPlex` and let's say my public address is `https://seanwlk.lan`. Suming up with the HTTP GET argument `title` and `key` (this is a private key of your choice that you put in `config.json` to restrict access to the endpoint only to who knows the key and avoiding random people putting stuff in your library) we get `https://seanwlk.lan/getOnPlex?key=YOUR_KEY_HERE&title=Movie Or Series Name` (You could use this for direct access from another application too instead of using the IFTTT assistant you can make your own)
- Configure as follows (but with your data) ![Listener2](https://raw.githubusercontent.com/seanwlk/voice-assist-downloader/master/docs/images/listener2.jpg)
- Click "Create Action"
- Make sure the applet is enabled

