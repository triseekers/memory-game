import random, pygame, sys
from pygame.locals import*

#Frames per second, speed of program
FPS = 30
#width in pixels
WINDOWWIDTH = 640
#hight in pixels
WINDOWHEIGHT = 480
#speed of a box to reveal and cover
REVEALSPEED = 8
#size of box
BOXSIZE = 40
#size of gap between boxes
GAPSIZE = 10
#columns of icons
BOARDWIDTH = 10
#rows of icons
BOARDHEIGHT = 7
assert(BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#colors
GRAY = (100, 100, 100)
BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = ( 0, 255, 0)
BLUE = ( 0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = ( 0, 255, 255)

BGCOLOR = BLACK
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

#shapes
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."

def main():
	global FPSCLOCK, DISPLAYSURF
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	#store x coordinate of mouse event
	mousex = 0
	#store y coordinate of mouse event
	mousey = 0
	pygame.display.set_caption("How's your Memory?")
	mainBoard = getRandomizedBoard()
	revealedBoxes = generateRevealedBoxesData(False)
	#stores the (x, y) of the first box clicked
	firstSelection = None
	DISPLAYSURF.fill(BGCOLOR)
	startGameAnimation(mainBoard)
	#main game loop
	while True:
		mouseClicked = False
		#drawing the window
		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(mainBoard, revealedBoxes)
		#event handling loop
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouseClicked = True
		boxx, boxy = getBoxAtPixel(mousex, mousey)
		if boxx != None and boxy != None:
			#the mouse is currently over a box
			if not revealedBoxes[boxx][boxy]:
				drawHighlightBox(boxx, boxy)
			if not revealedBoxes[boxx][boxy] and mouseClicked:
				revealBoxesAnimation(mainBoard, [(boxx, boxy)])
				#set the box as revealed
				revealedBoxes[boxx][boxy] = True
				#the current box was the first box clicked
				if firstSelection == None:
					firstSelection = (boxx, boxy)
				#the current box was the second clicked
				#check if there is a match between the two icons
				else:
					icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
					icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)
					if icon1shape != icon2shape or icon1color != icon2color:
						#icons dont match. Re-cover up both selections
						#1000ms = 1 sec
						pygame.time.wait(1000)
						coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
						revealedBoxes[firstSelection[0]][firstSelection[1]] = False
						revealedBoxes[boxx][boxy] = False
					#check if all pairs found
					elif hasWon(revealedBoxes):
						gameWonAnimation(mainBoard)
						pygame.time.wait(2000)
						#reset the board
						mainBoard = getRandomizedBoard()
						revealedBoxes = generateRevealedBoxesData(False)
						#show the fully unrevealed board for a second
						drawBoard(mainBoard, revealedBoxes)
						pygame.display.update()
						pygame.time.wait(1000)
						#replay the start game animation
						startGameAnimation(mainBoard)
					#reset firstSelection variable
					firstSelection = None
		#redraw the screen and wait a clock tick
		pygame.display.update()
		FPSCLOCK.tick(FPS)

def generateRevealedBoxesData(val):
	revealedBoxes = []
	for i in range(BOARDWIDTH):
		revealedBoxes.append([val] * BOARDHEIGHT)
	return revealedBoxes

def getRandomizedBoard():
	#get a list of every possible shape in every possible color
	icons = []
	for color in ALLCOLORS:
		for shape in ALLSHAPES:
			icons.append((shape, color))
	#randomized the order of the icon list
	random.shuffle(icons)
	#calculate how many icons are needed
	numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
	#make 2 of each
	icons = icons[:numIconsUsed] * 2
	random.shuffle(icons)

	#create the board data structure, with randomly placed icons
	board = []
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(icons[0])
			#remove the icons as we assign them
			del icons[0]
		board.append(column)
	return board

def splitIntoGroupsOf(groupSize, theList):
	#splits a list into a list of lists, where the inner lists have at
	#most groupSize number of items
	result = []
	for i in range(0, len(theList), groupSize):
		result.append(theList[i:i + groupSize])
	return result

def leftTopCoordsOfBox(boxx, boxy):
	#convert board coordinates to pixel coordinates
	left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
	top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
	return (left, top)

def getBoxAtPixel(x, y):
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = leftTopCoordsOfBox(boxx, boxy)
			boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
			if boxRect.collidepoint(x, y):
				return(boxx, boxy)
	return(None, None)

def drawIcon(shape, color, boxx, boxy):
	#syntactic sugar
	quarter = int(BOXSIZE * 0.25)
	half = int(BOXSIZE * 0.5)
	#get pixel coords from board coords
	left, top = leftTopCoordsOfBox(boxx, boxy)
	#draw the shapes
	if shape == DONUT:
		pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
		pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
	elif shape == SQUARE:
		pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
	elif shape == DIAMOND:
		pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE -1), (left, top + half)))
	elif shape == LINES:
		for i in range(0, BOXSIZE, 4):
			pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
			pygame.draw.line(DISPLAYSURF, color, (left + i , top  + BOXSIZE - 1), (left +  BOXSIZE - 1, top + i))
	elif shape == OVAL:
		pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))

def getShapeAndColor(board, boxx, boxy):
	#shape value for x, y spot is stored in board[x][y][0]
	#color value for x, y spot is stored in board[x][y][1]
	return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
	#draws boxes being covered
	for box in boxes:
		left, top = leftTopCoordsOfBox(box[0], box[1])
		pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
		shape, color = getShapeAndColor(board, box[0], box[1])
		drawIcon(shape, color, box[0], box[1])
		#only draw the cover if there is an coverage
		if coverage > 0:
			pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
	pygame.display.update()
	FPSCLOCK.tick(FPS)

def revealBoxesAnimation(board, boxesToReveal):
	#do the 'box reveal' animation
	for coverage in range(BOXSIZE, (-REVEALSPEED) -1, -REVEALSPEED):
		drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
	#do the 'box cover' animation
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
	#draws all of the boxes in their covered or revealed state
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = leftTopCoordsOfBox(boxx, boxy)
			if not revealed[boxx][boxy]:
				#draw covered box
				pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
			else:
				#draw the 'revealed' icon
				shape, color = getShapeAndColor(board, boxx, boxy)
				drawIcon(shape, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
	left, top = leftTopCoordsOfBox(boxx, boxy)
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
	#randomly reveal the boxes 8 at a time
	coveredBoxes = generateRevealedBoxesData(False)
	boxes = []
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			boxes.append((x, y))
	random.shuffle(boxes)
	boxGroups = splitIntoGroupsOf(8, boxes)
	drawBoard(board, coveredBoxes)
	for boxGroup in boxGroups:
		revealBoxesAnimation(board, boxGroup)
		coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
	#flash the background color when the player has won
	coveredBoxes = generateRevealedBoxesData(True)
	color1 = LIGHTBGCOLOR
	color2 = BGCOLOR
	for i in range(13):
		#swap color
		color1, color2 = color2, color1
		DISPLAYSURF.fill(color1)
		drawBoard(board, coveredBoxes)
		pygame.display.update()
		pygame.time.wait(300)

def hasWon(revealedBoxes):
	#returns True if all the boxes have been revealed, otherwise False
	for i in revealedBoxes:
		if False in i:
			#return false if any boxes are covered
			return False
	return True

if __name__ == '__main__':
	main()