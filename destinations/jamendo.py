import os
import requests
import shutil
import webbrowser

from destinations.destination import Destination

class Jamendo(Destination):
    name = "Jamendo"

    def __init__(self, config):
        self.config = config

    def save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        self.name = 'Jamendo'
        endpoint = 'https://api.jamendo.com/v3.0/tracks/?format=json&limit=1&client_id=' + \
            self.config['client_id']
        q = '&artist_name=' + track.artist.name + '&name=' + track.title
        url = endpoint + q
        r = requests.get(url)
        response = r.json()
        if response['headers']['results_count'] < 1:
            # track not found
            return (False, "Jamendo search returned no results for {}".format(q))

        download_url = response['results'][0]['audiodownload']
        if 'save_directory' in self.config:
            # download the song directly to the specified location
            filename = os.path.join(self.config['save_directory'],
                                    '{} - {}.mp3'.format(track.artist.name, track.title))
            r = requests.get(download_url, stream=True)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                return (True, "Saved from Jamendo to {}".format(filename))
            else:
                return (False, "Jamendo download URL returned status {}".format(r.status_code))
        else:
            # punt the problem to someone else: open a 'Save As' dialogue via
            # the browser.
            webbrowser.open(download_url)
            return (True, "Opened Jamendo download URL")
        
