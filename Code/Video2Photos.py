import os

"""
This python file creates the photos from a video using ffmpeg
"""

def video_2_photo(name_video):

    DIR = 'PhotosFromVideo/'
    # First remove the directory if existing and create the directory
    os.system('rm -r '+ DIR)
    os.system('mkdir '+ DIR)


    # Then create the photos in the directory
    os.system('ffmpeg -i '+ name_video +' -ss 00:00:00.000 '+ DIR+'Photo%4d.jpg -hide_banner')
