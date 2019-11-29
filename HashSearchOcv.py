# Package Import
from imutils import paths
import argparse
import time
import sys
import cv2
import os

def dhash(image, hashSize=8):
	# Input image resize, add a column (width) then compute the horizontal gradient
	resized = cv2.resize(image, (hashSize + 1, hashSize))
 
	# Compute the horizontal gradient between adjacent column pixels
	diff = resized[:, 1:] > resized[:, :-1]
 
	# Convert the image to a hash
	return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

# Parse and construct the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--destination", required=True, help="destination image directories")
ap.add_argument("-s", "--source", required=True, help="original set to search")
args = vars(ap.parse_args())

# Get the paths to destination and source images 
print("[INFO] Computing destination hashes...")
destPaths = list(paths.list_images(args["destination"]))
srcPaths = list(paths.list_images(args["source"]))
 
# On a Unix remove the space from any filenames
if sys.platform != "win32":
	destPaths = [p.replace("\\", "") for p in destPaths]
	srcPaths = [p.replace("\\", "") for p in srcPaths]

# Get subdirectories for the source paths
# Initialize the dictionary that will map the hash and corresponding image
# Start the timer
BASE_PATHS = set([p.split(os.path.sep)[-2] for p in srcPaths])
Destination = {}
sTime = time.time()

# loop over the destination paths
for p in destPaths:
	# load the image from disk
	image = cv2.imread(p)
 
	# When image is None then we couldn't load it from disk (skip it)
	if image is None:
		continue
 
	# Convert the image to grayscale and compute the hash
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	imageHash = dhash(image)
 
	# Update the destination dictionary
	l = Destination.get(imageHash, [])
	l.append(p)
	Destination[imageHash] = l

# Show timing for hashing, then start computing source image hashes
print("[INFO] Processed {} images in {:.2f} seconds".format(len(Destination), time.time() - sTime))
print("[INFO] Computing source hashes:")

# Loop over the source paths
for p in srcPaths:
	# Load the image from disk
	image = cv2.imread(p)
 
	# When image is None then we couldn't load it from disk (skip it)
	if image is None:
		continue

	# Convert the image to grayscale and compute the hash
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	imageHash = dhash(image)
	print("[SOURCE] ", p, " [FINGERPRINT] ", imageHash)
	# Get all the image paths that match the hash
	matchPaths = Destination.get(imageHash, [])

	# Loop over all matched paths
	for matchPath in matchPaths:
		# Extract the subdirectory from the image path
		b = p.split(os.path.sep)[-2]
		print("[COPIED] ", matchPaths, " [FINGERPRINT] ", imageHash)
		
		# If the subdirectory exists in the base path for the source images, remove it
		if b in BASE_PATHS:
			BASE_PATHS.remove(b)			
			continue

		print("[MISSING FILES] Listed below:")
		# Print missing files
		if matchPaths is None:
			print("[DIRECTORY] ", p, " [FINGERPRINT] ", imageHash)
			continue
# python .\HashSearchOcv.py --destination .\images --source .\hashtst
