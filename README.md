# Tileset-image-to-C-Array
This is for tilesets with rectangular tiles.
This is a Python3 program which uses the modules: PIL, enum, argparse

## Example Use
If you are on Windows:
```
python .\main.py -i .\tileset.png -x 16 -y 16 -c ARGB8888
```

## Output
The program will calculate how many tiles are in a row and also in a column depending on the supplied -x and -y arguments. Based on this, the total number of tiles will also be computed.
The program outputs these on the terminal:
```
The number of tiles in a row is 27
The number of tiles in a column is 18
The total number of tiles is 486
```
The program will also output a file with the C 3d array. 

## Program Arguments
| Parameter		| Required		| Description		|
| ---		| ---		| ---		|
| -i --input		| Yes		| The image to be converted		|
| -x --x-size		| Yes		| The width of a single tile(The image x size should be divisible by this)		|
| -y --y-size		| Yes		| The height of a single tile(The image y size should be divisible by this)		|
| -c --color-format		| Yes		| The color format(Choices are: RGB565, RGB888, ARGB8888)		|
| -o --output		| No		| The name of the output file(Defaults to "tilesToCArray.txt")		|
| -s --scan-direction		| No		| The scan direction for the image input(Choices are: LEFT_RIGHT_TOP_BOTTOM, RIGHT_LEFT_TOP_BOTTOM, LEFT_RIGHT_BOTTOM_TOP, RIGHT_LEFT_BOTTOM_TOP)		|
| -a --array-name		| No		| The name of the C array(Defaults to "tileset")		|
| -h --help		| No		| Show the help message		|