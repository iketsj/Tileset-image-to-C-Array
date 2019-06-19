from PIL import Image
from enum import Enum
import argparse



class TileSizeIndex(Enum):
	X = 0
	Y = 1

class ColorChannelIndexForPIL(Enum):
	RED = 0
	GREEN = 1
	BLUE = 2
	ALPHA = 3


class ColorChannelBitOffset(Enum):
	ARGB8888_ALPHA = 24
	ARGB8888_RED = 16
	ARGB8888_GREEN = 8
	ARGB8888_BLUE = 0
	
	RGB565_RED = 11
	RGB565_GREEN = 5
	RGB565_BLUE = 0

	RED5 = 3
	GREEN6 = 2
	BLUE5 = 3


class ScanLimitsInfoIndex(Enum):
	START = 0
	END = 1
	STEP = 2



def main():
	
	args = parse_args()
	
	if(args.output == None):
		outputFileName = "tilesToCArray.txt"
	else:
		outputFilename = args.output

	if(args.scan_direction == None):
		scanDirection = "LEFT_RIGHT_TOP_BOTTOM"
	else:
		scanDirection = args.scan_direction

	if(args.array_name == None):
		arrayName = "tileset"
	else:
		arrayName = args.array_name
		
	sizeOfATile = (args.x_size, args.y_size)

	image = Image.open(args.input).convert("RGBA")
	imagePixels = image.load()

	check_image_size_divisibility(image.width, image.height, args.x_size, args.y_size)

	numberOfTilesInARow = image.width // sizeOfATile[TileSizeIndex.X.value]
	numberOfTilesInAColumn = image.height // sizeOfATile[TileSizeIndex.Y.value]

	tiles, totalNumberOfTiles = get_tile_pixel_values_and_total_number_of_tiles(numberOfTilesInARow, numberOfTilesInAColumn, sizeOfATile, imagePixels, scanDirection)

	print("The number of tiles in a row is {0}".format(numberOfTilesInARow))
	print("The number of tiles in a column is {0}".format(numberOfTilesInAColumn))
	print("The total number of tiles is {0}".format(totalNumberOfTiles))

	tiles = convert_tiles_to_color_format(tiles, totalNumberOfTiles, args.color_format)

	outputString = convert_tiles_to_C_3d_array(totalNumberOfTiles, tiles, sizeOfATile, arrayName, args.color_format)

	with open(outputFileName, "w") as outputFile:
		outputFile.write(outputString)


def convert_tiles_to_C_3d_array(totalNumberOfTiles, tiles, sizeOfATile, arrayName, colorFormat):

	currentArrayIndex = 0
	outputString = ""
	indentation = " " * 4
	currentTileIteration = 0

	if(colorFormat == "RGB565"):
		dataType = "uint16_t"
		hexStringLength = 4
	elif(colorFormat == "RGB888" or colorFormat == "ARGB8888"):
		dataType = "uint32_t"
		hexStringLength = 8

	arrayDeclarationString = "const {0} {1} [{2}][{3}][{4}] = {{".format(dataType, arrayName, totalNumberOfTiles, sizeOfATile[TileSizeIndex.Y.value], sizeOfATile[TileSizeIndex.X.value])
	lengthOfArrayDeclarationString = len(arrayDeclarationString)
	outputString += arrayDeclarationString

	for tile in tiles:
		outputString += "\n"
		secondNestIndentation = (lengthOfArrayDeclarationString * ' ') + indentation + "{"
		lengthOfFirstNestIndentation = len(secondNestIndentation)
		outputString += secondNestIndentation
		for i in range(0, sizeOfATile[TileSizeIndex.Y.value]):
			outputString += "\n"
			outputString += (lengthOfFirstNestIndentation * ' ')
			outputString += indentation
			outputString += "{"
			for j in range(0, sizeOfATile[TileSizeIndex.X.value]):
				outputString += "0x{0:0{1}x}".format(tile[(i * sizeOfATile[TileSizeIndex.X.value]) + j], hexStringLength)
				if(j == (sizeOfATile[TileSizeIndex.X.value] - 1)):
					outputString += ""
				else:
					outputString += ", "
			outputString += "}"
			if(i == (sizeOfATile[TileSizeIndex.Y.value] - 1)):
				outputString += ""
			else:
				outputString += ", "
		outputString += "\n"
		outputString += (lengthOfArrayDeclarationString * ' ')
		outputString += indentation
		outputString += "}"
		currentTileIteration = currentTileIteration + 1
		if(currentTileIteration == len(tiles)):
			outputString += ""
		else:
			outputString += ", "
		outputString += "\n"
	outputString += "};\n"

	return outputString


def convert_tiles_to_color_format(tiles, totalNumberOfTiles, colorFormat):

	tilesPixelValueList = [[] for i in range(totalNumberOfTiles)]

	if(colorFormat == "RGB565"):
		tilesPixelValueList = convert_tiles_list_to_rgb565_list(tiles, totalNumberOfTiles)
	elif(colorFormat == "RGB888"):
		tilesPixelValueList = convert_tiles_list_to_rgb888_list(tiles, totalNumberOfTiles)
	elif(colorFormat == "ARGB8888"):
		tilesPixelValueList = convert_tiles_list_to_argb8888_list(tiles, totalNumberOfTiles)

	return tilesPixelValueList


def convert_tiles_list_to_rgb565_list(tiles, totalNumberOfTiles):

	tilesPixelValueList = [[] for i in range(totalNumberOfTiles)]
	pixelValueORED = 0
	currentTileIndex = 0

	for tile in tiles:
		for pixelValue in tile:
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.RED.value] >> ColorChannelBitOffset.RED5.value) << ColorChannelBitOffset.RGB565_RED.value
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.GREEN.value] >> ColorChannelBitOffset.GREEN6.value) << ColorChannelBitOffset.RGB565_GREEN.value
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.BLUE.value] >> ColorChannelBitOffset.BLUE5.value) << ColorChannelBitOffset.RGB565_BLUE.value
			tilesPixelValueList[currentTileIndex].append(pixelValueORED)
			pixelValueORED = 0
		currentTileIndex = currentTileIndex + 1

	return tilesPixelValueList


def convert_tiles_list_to_rgb888_list(tiles, totalNumberOfTiles):

	tilesPixelValueList = [[] for i in range(totalNumberOfTiles)]
	pixelValueORED = 0
	currentTileIndex = 0

	for tile in tiles:
		for pixelValue in tile:
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.RED.value] << ColorChannelBitOffset.ARGB8888_RED.value)
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.GREEN.value] << ColorChannelBitOffset.ARGB8888_GREEN.value)
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.BLUE.value] << ColorChannelBitOffset.ARGB8888_BLUE.value)
			tilesPixelValueList[currentTileIndex].append(pixelValueORED)
			pixelValueORED = 0
		currentTileIndex = currentTileIndex + 1

	return tilesPixelValueList


def convert_tiles_list_to_argb8888_list(tiles, totalNumberOfTiles):

	tilesPixelValueList = [[] for i in range(totalNumberOfTiles)]
	pixelValueORED = 0
	currentTileIndex = 0

	for tile in tiles:
		for pixelValue in tile:
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.ALPHA.value] << ColorChannelBitOffset.ARGB8888_ALPHA.value)
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.RED.value] << ColorChannelBitOffset.ARGB8888_RED.value)
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.GREEN.value] << ColorChannelBitOffset.ARGB8888_GREEN.value)
			pixelValueORED |= (pixelValue[ColorChannelIndexForPIL.BLUE.value] << ColorChannelBitOffset.ARGB8888_BLUE.value)
			tilesPixelValueList[currentTileIndex].append(pixelValueORED)
			pixelValueORED = 0
		currentTileIndex = currentTileIndex + 1

	return tilesPixelValueList


def parse_args():

	parser = argparse.ArgumentParser(description="Convert a tileset image to C arrays")
	parser.add_argument("-i", "--input", metavar="", required=True, help="The image to be converted")
	parser.add_argument("-x", "--x-size", metavar="", required=True, type=int, help="The width of a single tile")
	parser.add_argument("-y", "--y-size", metavar="", required=True, type=int, help="The height of a single tile")
	parser.add_argument("-c", "--color-format", metavar="", required=True, choices=["RGB565", "RGB888", "ARGB8888"], help="The color format")
	parser.add_argument("-o", "--output", metavar="", help="The name of the output file")
	parser.add_argument("-s", "--scan-direction", metavar="", choices=["LEFT_RIGHT_TOP_BOTTOM", "RIGHT_LEFT_TOP_BOTTOM", "LEFT_RIGHT_BOTTOM_TOP", "RIGHT_LEFT_BOTTOM_TOP"], help="The scan direction for the image input")
	parser.add_argument("-a", "--array-name", metavar="", help="The name of the C array")
	args = parser.parse_args()
	
	return args


def get_tile_pixel_values_and_total_number_of_tiles(numberOfTilesInARow, numberOfTilesInAColumn, sizeOfATile, imagePixels, scanDirection):

	totalNumberOfTiles = numberOfTilesInARow * numberOfTilesInAColumn

	if(scanDirection == "LEFT_RIGHT_TOP_BOTTOM"):
		y1ScanLimits = 0, sizeOfATile[TileSizeIndex.Y.value] * numberOfTilesInAColumn, sizeOfATile[TileSizeIndex.Y.value]
		y2ScanLimits = 0,  sizeOfATile[TileSizeIndex.Y.value], 1
		x1ScanLimits = 0, sizeOfATile[TileSizeIndex.X.value] * numberOfTilesInARow, sizeOfATile[TileSizeIndex.X.value]
		x2ScanLimits = 0, sizeOfATile[TileSizeIndex.X.value], 1
	elif(scanDirection == "RIGHT_LEFT_TOP_BOTTOM"):
		y1ScanLimits = 0, sizeOfATile[TileSizeIndex.Y.value] * numberOfTilesInAColumn, sizeOfATile[TileSizeIndex.Y.value]
		y2ScanLimits = 0,  sizeOfATile[TileSizeIndex.Y.value], 1
		x1ScanLimits = (sizeOfATile[TileSizeIndex.X.value] * numberOfTilesInARow) - 1, -1, -(sizeOfATile[TileSizeIndex.X.value])
		x2ScanLimits = (sizeOfATile[TileSizeIndex.X.value]) -1, -1, -1
	elif(scanDirection == "LEFT_RIGHT_BOTTOM_TOP"):
		y1ScanLimits = (sizeOfATile[TileSizeIndex.Y.value] * numberOfTilesInAColumn) -1, -1, -(sizeOfATile[TileSizeIndex.Y.value])
		y2ScanLimits = (sizeOfATile[TileSizeIndex.Y.value]) -1, -1, -1
		x1ScanLimits = 0, sizeOfATile[TileSizeIndex.X.value] * numberOfTilesInARow, sizeOfATile[TileSizeIndex.X.value]
		x2ScanLimits = 0, sizeOfATile[TileSizeIndex.X.value], 1
	elif(scanDirection == "RIGHT_LEFT_BOTTOM_TOP"):
		y1ScanLimits = (sizeOfATile[TileSizeIndex.Y.value] * numberOfTilesInAColumn) -1, -1, -(sizeOfATile[TileSizeIndex.Y.value])
		y2ScanLimits = (sizeOfATile[TileSizeIndex.Y.value]) -1, -1, -1
		x1ScanLimits = (sizeOfATile[TileSizeIndex.X.value] * numberOfTilesInARow) - 1, -1, -(sizeOfATile[TileSizeIndex.X.value])
		x2ScanLimits = (sizeOfATile[TileSizeIndex.X.value]) -1, -1, -1

	tiles = get_tile_pixel_values(numberOfTilesInARow, numberOfTilesInAColumn, totalNumberOfTiles, imagePixels, y1ScanLimits, y2ScanLimits, x1ScanLimits, x2ScanLimits)

	return tiles, totalNumberOfTiles


def get_tile_pixel_values(numberOfTilesInARow, numberOfTilesInAColumn, totalNumberOfTiles, imagePixels, y1ScanLimits, y2ScanLimits, x1ScanLimits, x2ScanLimits):

	tiles = [[] for i in range(totalNumberOfTiles)]

	indexOfATile = 0
	tileNumberOffset = 0
	currentRow = 0
	currentColumn = 0
	
	for y1 in range(y1ScanLimits[ScanLimitsInfoIndex.START.value], y1ScanLimits[ScanLimitsInfoIndex.END.value], y1ScanLimits[ScanLimitsInfoIndex.STEP.value]):
		tileNumberOffset = currentRow * numberOfTilesInARow
		for y2 in range(y2ScanLimits[ScanLimitsInfoIndex.START.value], y2ScanLimits[ScanLimitsInfoIndex.END.value], y2ScanLimits[ScanLimitsInfoIndex.STEP.value]):
			indexOfATile = 0
			for x1 in range(x1ScanLimits[ScanLimitsInfoIndex.START.value], x1ScanLimits[ScanLimitsInfoIndex.END.value], x1ScanLimits[ScanLimitsInfoIndex.STEP.value]):
				indexOfATile = tileNumberOffset + currentColumn
				for x2 in range(x2ScanLimits[ScanLimitsInfoIndex.START.value], x2ScanLimits[ScanLimitsInfoIndex.END.value], x2ScanLimits[ScanLimitsInfoIndex.STEP.value]):
					tiles[indexOfATile].append(imagePixels[x1 + x2, y1 + y2])
				currentColumn = currentColumn + 1
			currentColumn = 0
		currentRow = currentRow + 1

	return tiles


def check_image_size_divisibility(imageXSize, imageYSize, tileXSize, tileYSize):

	if(imageXSize % tileXSize != 0):
		print("X size not divisible!")
		exit()
	if(imageYSize % tileYSize != 0):
		print("Y size not divisible!")
		exit()
		

if __name__ == '__main__':
	main()
	