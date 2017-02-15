# evenTiler
A simple script for tiling images into a single image. The script is a smith of the air... between the tiles you see...

Usage
---
`python tiler.py -i "c:/tmp/star wars V/" -o "test.png" --outputHeight 2000  --crop --pickImages 500`

Pick the first 500 images from your directory with star wars V images and place the tiles in order (row-by-row from from left to right). The tile has a height of 2000 pixels and any images that won't fit, are cropped (from upper left corner).
