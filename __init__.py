import configparser
import pylast

from destinations import fma, soundcloud, spotify, jamendo, youtube
from destinations import soundcloud_download


def most_current_track(last_fm_user):
    '''
    Gets either the now playing track or the most recently played track.
    '''
    now_playing = last_fm_user.get_now_playing()
    if now_playing:
        return now_playing
    try:
        # now playing track is excluded from get_recent_tracks by pylast,
        # so in the event of unfortunate timing, we will need it to
        # initially fetch two tracks from the api in order to have a
        # nonempty list. Assume the API will never mark two tracks as
        # "now playing" in one response.
        return last_fm_user.get_recent_tracks(limit=2)[0].track
    except IndexError:
        # No tracks returned
        return None


def save_track(track, destinations):
    '''
    Loop through each destination and attempt to save the given track.
    '''
    for destination in destinations:
        try:
            success, message = destination.save(track)
            print(message)
            if success:
                return True
        except Exception as e:
            # This looks bad, but there's a real reason to just eat the exception.
            # For whatever reason, saving to one destination caused an error. This is not
            # cause for giving up on the other destinations.
            print(str(e))
            print('Could not save to ' + destination.name)
    return False


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # last.fm initialization
    last_fm = config['Last.fm']
    ln = pylast.get_lastfm_network(api_key=last_fm['api_key'])
    user = pylast.User(last_fm['username'], ln)

    # The order these appear in this list will determine the order of preference.
    # If saving to one destination succeeds, no others will be tried.
    destinations = [
        # Highest priority: The ability to download the track directly.
        # Try the services with better search capabilities first.
        jamendo.Jamendo(config['Jamendo']),
        fma.FMA(config['Free Music Archive']),
        soundcloud_download.SoundcloudDownload(config['Soundcloud']),
        # Failing that, try to save to a streaming music service
        spotify.Spotify(config['Spotify']),
        soundcloud.Soundcloud(config['Soundcloud']),
        # Last resort: maybe it's available in video form
        youtube.Youtube(config['YouTube'])
    ]
    # Main input loop
    while True:
        input('\nPress enter to save song')
        # Fetch the song from the Last.fm api
        track = most_current_track(user)
        if not track:
            print('Could not get a track from Last.fm.')
            continue
        print(track.artist.name, " - ", track.title)

        success = save_track(track, destinations)
        if not success:
            print('Could not save to any destination.')

if __name__ == '__main__':
    main()
