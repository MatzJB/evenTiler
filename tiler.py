from PIL import Image
import argparse
#import ctypes
import random
#import getopt
import time
import math
import sys
import os
from random import randint

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True  # fixes issues with some images


# nicked from http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# Print iterations progress


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='#'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = (
        "{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + ' ' * (length - filledLength)
    sys.stdout.write('\r%s [%s] %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    # Print New Line on Complete
    if iteration == total:
        print ""


# Todo: add support of padding around mosaics?
def createImageWall(tiles, resolution, imgFiles, imgSize, crop=False):
    barLength = 40  # length of progress bar
    wTile, hTile = tiles
    wTotal, hTotal = resolution
    wMoselNew, hMoselNew = imgSize
    imageWall = Image.new("RGBA", (wTotal, hTotal))
    moselInd = 0  # keeping track of current tile
    for i in range(0, hTile):
        for j in range(0, wTile):
            if moselInd == len(imgFiles):  # found the last one
                return imageWall
            filename = imgFiles[moselInd]
            img = Image.open(filename)
            if crop:
                scale = (1.0*wMoselNew)/img.size[0]
                wMoselNewCrop = int(scale*img.size[0])
                hMoselNewCrop = int(scale*img.size[1])
                # todo: add padding to crop image
                img = img.resize(
                    (wMoselNewCrop, hMoselNewCrop), Image.ANTIALIAS)
                img = img.crop((0, 0, wMoselNew, hMoselNew))
            else:
                img = img.resize((wMoselNew, hMoselNew), Image.ANTIALIAS)
            imageWall.paste(img, (j*wMoselNew, i*hMoselNew))
            moselInd += 1
            if randint(0, 100) > 80:
                printProgressBar(
                    i*wTile+j, wTile*hTile, prefix='Progress:', suffix='Complete', length=barLength)
    printProgressBar(
        1, 1, prefix='Progress:', suffix='Complete', length=barLength)
    return imageWall


def getFilesFromDir(path, nFiles):
    from os import walk
    files = []
    for (path, dirnames, filenames) in walk(path):
        for filename in filenames:
            if len(files) < nFiles and filename.endswith('.jpg'):
                files.append(os.path.join(path, filename))
            else:
                return files
        return files  # when this dir has been collected


# check tile and ratio, getting tile in the same ratio as image is not the
# same as final ratio
parser = argparse.ArgumentParser(description='Program used to tile images \
                              given a directory of images. Note: tiling is based off of the ratio of the first image in the specified directory.')
parser.add_argument('-r', help="randomize image order",
                    action='store_true')
parser.add_argument('-v', help="verbose output",
                    action='store_true')
parser.add_argument("--crop", help="crop images to fit",
                    action='store_true')
parser.add_argument("-i", "--inputPath",
                    help="path to images", type=str,
                    default='.', required=True)
parser.add_argument("-o", "--outputFilename",
                    help="output filename", type=str,
                    default='./output.png', required=True)
parser.add_argument("--outputHeight",
                    help="height of rendered image", type=int,
                    default=720, required=False)
parser.add_argument("--pickImages",
                    help="specify how many images that is used",
                    type=int, required=False)
parser.add_argument("--wallAspectRatio",
                    help="specify aspect ratio of wall",
                    type=float, required=False)
parser.add_argument("--moselAspectRatio",
                    help="specify aspect ratio of mosaic elements",
                    type=float, required=False)

args = vars(parser.parse_args())
crop = args['crop']
randomize = args['r']
verbose = args['v']
moselDir = args['inputPath']
hTotal = args['outputHeight']
outputFilename = args['outputFilename']
pickImages = args['pickImages']
#wallAspectRatio = args['wallAspectRatio']
#moselAspectRatio = args['moselAspectRatio']

# check that it is ending with pathsep
imgFiles = getFilesFromDir(moselDir, pickImages)
if len(imgFiles) == 0:
    raise ValueError("No files found")

if verbose:
    print "sanity checking images..."

# sanity check images:
for file in imgFiles:

    try:
        img = Image.open(file)
        img = img.resize((3, 3), Image.ANTIALIAS)
    except:
        print "An error occured in reading {}".format(file)
        imgFiles.remove(file)
        # continue

if verbose:
    print "number of images: {}".format(len(imgFiles))

if randomize:
    if verbose:
        print "shuffling images"
    random.shuffle(imgFiles)

sqrtLen = math.sqrt(len(imgFiles))
hTile = int(math.ceil(math.sqrt(len(imgFiles))))

# lower number of tiles given number of images
wTile = int(math.floor(len(imgFiles)/hTile))
# given aspectRatio how do we get tiles?
img = Image.open(imgFiles[1])
wMosel, hMosel = img.size
hMoselNew = math.floor(hTotal/hTile)
ratio = (1.0*wMosel)/hMosel
# if aspectRatio is not None:  # overriding mosel aspect ratio
#   ratio = aspectRatio
wMoselNew = int(hMoselNew*ratio)
hMoselNew = int(hMoselNew)

if verbose:
    print " original mosel size: {}x{}".format(wMosel, hMosel)
    print " calculated mosel size: {}x{}".format(wMoselNew, hMoselNew)
    print " ratio: {}".format(ratio)
    print " tiling: {}x{}".format(wTile, hTile)

wTotal = wMoselNew*wTile  # int(math.floor(ratio*hTotal))

# todo: warning if RAM is low
# psutil.virtual_memory()

diff = int(math.fabs(wTile*hTile - len(imgFiles)))

if hMoselNew > hMosel:
    print("Warning: Mosels are resized to be larger than the source.")

if diff != 0:  # otherwise it is perfect
    if len(imgFiles) > wTile*hTile:
        print(
            "Warning: not optimal tiling. {} images were not picked".format(diff))
    else:
        print(
            "Warning: not optimal tiling, {} images are missing.".format(diff))

# tiles = (wTile, hTile)
# resolution = (wTotal, hTotal)
imgSize = (wMoselNew, hMoselNew)
imageWall = createImageWall(
    (wTile, hTile), (wTotal, hTotal), imgFiles, imgSize, crop)

sys.stdout.write("saving image...")
sys.stdout.flush()
imageWall.save(outputFilename)
sys.stdout.write("done.")
