# coding: utf-8
"""
########
BadgeBot
########
by David Jonathan Ross
based on a design by Nick Sherman

Run this in Drawbot (drawbot.com)
"""
import unicodedata
import string
from random import choice
import os
from drawBot import *
import csv
from easing_functions import *
from itertools import cycle


def hex2rgb(myHexString):
    # this is a function that converts a hex string ‘#FF0000’ to a list of RGB values
    # remove any pound sign that precedes the string so we are just looking at the
    # numbers 0–9 and letters A–F
    myHexString = myHexString.lstrip('#')
    # determine how many characters are in the hex string
    # by making this a variable we can deal with both RGB and RGBA values
    myHexLength = len(myHexString)
    # create an empty list to catch the color values that we process
    myColors = []
    # now we will loop through a range of numbers between 0 and the length of our hex string
    # but will skip every other number so that we process the characters in pairs
    for myIndex in range(0, myHexLength, 2):
        # use in index to slice the string
        myHexColorPair = myHexString[myIndex : myIndex + 2]
        # by converting to an integer with base 16
        # we get the value between 0 and 255
        my255ColorValue = int(myHexColorPair, 16)
        # drawbot wants the value between 0 and 1, so we divide by 255
        myColorValue = my255ColorValue / 255
        # now we add the color value to our list
        myColors.append(myColorValue)
    # when we are done, return all color values we have found as a tuple
    return tuple(myColors)
def fillHex(myHexValue):
    # this function uses hex2rgb to convert the value, and then applies the fill
    fill(*hex2rgb(myHexValue))
def strokeHex(myHexValue):
    # this function uses hex2rgb to convert the value, and then applies the stroke
    stroke(*hex2rgb(myHexValue))


colorPalette = {
    'background': hex2rgb('#e8cde9'),
    'pattern': hex2rgb('#a62116'),
    'name': hex2rgb('#ea3323'),
    'shine': hex2rgb('#FFFFFF'),
    'shade': hex2rgb('#7d1d17'),
    }

# keep track of folks whose names will not be on three lines
linebreakExceptions = [] 

# black bar at the bottom with affiliation
showCompany = True

## VARIABLES

pt = 72                # 72pt in an inch
black = 0, 0, 0, 1    # black
white = 1, 1, 1, 1    # white

# Get the path to an installed font by name
nameFont = "../fonts/Mayonnaise-Desktop/Mayonnaise-Extra-Black.otf"
nameFontShade = "../fonts/Mayonnaise-Desktop/Mayonnaise-Volume-Shadow.otf"
nameFontShine = "../fonts/Mayonnaise-Desktop/Mayonnaise-Volume-Shine.otf"
patternFont = 'Crackly-Regular'

nameFonts = {
    'shade': nameFontShade,
    'name': nameFont,
    'shine': nameFontShine
    }

companyFont = 'fonts/HEX Franklin v0.2 Variable 2022-06-10.ttf'

# Released by DJR under the BSD license 
def norm(value, start, stop):
	"""
	Return the interpolation factor (between 0 and 1) of a VALUE between START and STOP.
	See also: https://processing.org/reference/norm_.html
	"""
	return float(value-start) / float(stop-start)
	
def lerp(start, stop, amt):
	"""
	Interpolate using a value between 0 and 1
	https://processing.org/reference/lerp_.html
	"""
	return start + (stop-start) * amt

def remap(value, start1, stop1, start2, stop2, clamp=False):
    """
    Re-maps a number from one range to another.
    """
    factor = norm(value, start1, stop1)
    if clamp:
        if factor < 0: factor = 0
        if factor > 1: factor = 1
    return lerp(start2, stop2, factor)


def parseRowData(rowData, colHeaders):
    # a quick way to just get the rows we need from the eventbrite csv
    firstName = rowData[colHeaders.index('First Name')]
    lastName = rowData[colHeaders.index('Last Name')]
    company = rowData[colHeaders.index('Company')]
    return firstName, lastName, company

# NOT USING THIS
# We use this to add space between the lines. This list is made for Stilla.
# It may be different for other fonts!
descenders = ['Q', 'q']
ascenders = [u'Ñ', u'Á', u'À', u'Ú', u'Ó', u'É', u'é']



def drawCompany(company, companySize, companyWidth, companyHeight, textColor, bottomMargin=0, bleedLeft=0, bleedRight=0):
    
    trackValue = 0.15
    wordSpaceTracking = .75
    
    fill(0)
    rect(-bleedLeft, 0, width()+bleedLeft+bleedRight, companyHeight)
    
    companyFs = FormattedString('', font=companyFont, fontSize=companySize, fill=(1, 1, 1), lineHeight=companySize, fontVariations={'wdth': 93}, tracking=trackValue)
    for companyChar in company:
        if companyChar == ' ':
            companyFs.append(companyChar, tracking=wordSpaceTracking)
            companyFs.tracking(trackValue)
        else:
            companyFs.append(companyChar)
    
    cw, ch = textSize(companyFs, width=companyWidth)
    if cw > companyWidth-50:
        companyFs = FormattedString(company, font=companyFont, fontSize=companySize, fill=(1, 1, 1), lineHeight=companySize, fontVariations={'wdth': 80})

        
    fill(0, 1, 0, .5)
    text(companyFs, (w/2, bottomMargin), align="center")

def capitalize(theText):
    # convert text to uppercase, and deal with McNames => McNAMES
    try:
        if theText[0:2] in ['Mc', 'La'] and theText[2] == theText[2].upper() and theText[3] == theText[3].lower():
            theText = theText[0:2] + theText[2:].upper()
        else:
            theText = theText.upper()
    except:
        theText = theText.upper()
    return theText

def drawName(firstName, lastName, boxWidth, boxHeight, bleedLeft=0, bleedRight=0, colorIndex=0):
    # this function draws the attendee’s name
    with savedState():
        firstName = firstName.strip()
        lastName = lastName.strip()
        # ‘NFC’, ‘NFKC’, ‘NFD’, and ‘NFKD’
        line1 = capitalize(unicodedata.normalize('NFC', firstName))
        line2 = capitalize(unicodedata.normalize('NFC', lastName))
        
        # depending on the name, figure out how many lines it should appear on
        # the CSV provides firstName and lastName, we will always break between those
        oneLine = line1 + ' ' + line2
        twoLines = line1 + '\n' + line2
        # figure out if either field has multiple words
        line1words = line1.split(' ')
        line2words = line2.split(' ')
        # if a field has multiple words, by default we will break
        # but if any word is less than 4 chars, keep them
        doLine1Split = True
        doLine2Split = True
        for word in line1words:
            if len(word) < 4:
                doLine1Split = False
        for word in line2words:
            if len(word) < 4:
                doLine2Split = False
                                
        # if the total name plus space is less than 6 chars, draw it on one line
        if len(oneLine) < 6 or not line1 or not line2:
            theName = oneLine
            if theName not in linebreakExceptions: linebreakExceptions.append(theName)
        # if the two-line setting is particularly balanced, always draw it on two lines
        elif abs(len(line1) - len(line2)) < 3:
            theName = twoLines
        # if the first name has multiple words and should break
        elif len(line1words) > 1 and doLine1Split:
            # in a few situations, both names have multiple words and we will break to four lines
            if len(line2words) > 1 and doLine2Split:
                theName = '\n'.join(line1words) + '\n' + '\n'.join(line2words)#+ '!'
                if theName not in linebreakExceptions: linebreakExceptions.append(theName)
            # otherwise just break the first name
            else:
                theName = '\n'.join(line1words) + '\n' + line2 #+ '!'
                if theName not in linebreakExceptions: linebreakExceptions.append(theName)
        # just break the last name
        elif len(line2words) > 1 and doLine2Split:
            theName = line1 + '\n' + '\n'.join(line2words) #+ '!'
            if theName not in linebreakExceptions: linebreakExceptions.append(theName)
        # in all other cases, just use two lines
        else:
            theName = line1 + '\n' + line2 
        
        # how many lines did we end up with?
        lineCount = theName.count('\n')+1
        
        # set font size tolerances
        # need room at the top and bottom for the repeating slices
        maxFontSize = 84
        threeLineMaxSize = 70
        oneLineMaxSize = 160
        manyLineMaxFontSize = 50
        
        # set the font
        font(nameFont)
        
        # get the text proportions at 1pt
        fontSize(1)
        lineHeight(1)
        tw, th = textSize(theName)
        # calculate the font size using the proportions
        theFontSize = boxWidth/tw * .9
        
        # implement the font size tolerances
        if theFontSize > maxFontSize and '\n' in theName:
            theFontSize = maxFontSize
        if theFontSize > oneLineMaxSize and '\n' not in theName:
            theFontSize = oneLineMaxSize
        if theFontSize > threeLineMaxSize and lineCount >= 3:
            theFontSize = threeLineMaxSize 
        if lineCount >= 4 and theFontSize > manyLineMaxFontSize:
            theFontSize = manyLineMaxFontSize
        # add space between lines, factoring in overshoot
        lineGap = theFontSize*.06
        theLineHeight = theFontSize*.5 + lineGap

        # set the font size 
        font(nameFont, theFontSize)
        lineHeight(theLineHeight)

        # calculate the height of the text box
        textHeight = 0 + (theFontSize * .7 + lineGap) * lineCount

        # move to the center
        #translate(boxWidth/2, boxHeight/2)
 

        print(theName)
        for layer in ['shade', 'name', 'shine']:
            fill(*colorPalette[layer])
            font(nameFonts[layer])
            ts = textSize(theName)
            print(ts)
            xoffset = (boxWidth - ts[0])/2 + 5
            textBox(theName, (xoffset, 0, boxWidth, boxHeight-50), align="left")    
                
    
def drawBadge(w, h, firstName, lastName, company=None, setSize=True, DEBUG=False, backgroundColor=colorPalette['background'], phase=0, bleedLeft=0, bleedRight=0, bgIndex=None):
    """
    Draw one badge. This handles the positioning, and lets other functions do the drawing.
    """
    

    if setSize:
        newPage(w, h)
    boxWidth = w
    boxHeight = h
    with savedState():
        bp = BezierPath()
        bp.rect(-bleedLeft, 0, w+bleedLeft+bleedRight, h)
        clipPath(bp)

        # draw the background
        if backgroundColor:
            fill(*backgroundColor)
            rect(-bleedLeft, 0, w+bleedLeft+bleedRight, h)

        patternFontSize = 100
        font(patternFont, patternFontSize)
        lineHeight(patternFontSize)
        fill(*colorPalette['pattern'])
        patternText = 'AAAAAAAAAAAAAAA\n'*2
        textBox(patternText, (-boxWidth/2, -boxHeight/2, boxWidth*2, boxHeight*2))



        # print the company name
        companySize = 11
        affiliateBlock = companySize + 21
        affiliateBottomMargin = 14

        # draw the available space, in case we want to see it
        if DEBUG:
            fill(.8)
            rect(0, 0, boxWidth, boxHeight)
        # move things up if the company exists
        if company and showCompany:
            boxHeight = boxHeight - affiliateBlock
        else:
            affiliateBlock = 0
        with savedState():
            translate(0, affiliateBlock)
            fill(None)
            #stroke(1, 0, 0)
            #strokeWidth(10)
            #rect(0, 0, boxWidth, boxHeight)
            sw = drawName(firstName, lastName, boxWidth, boxHeight)
        
        # undo company move
        if company and showCompany:
            drawCompany(company, companySize, w, affiliateBlock, white, affiliateBottomMargin, bleedLeft, bleedRight)
            


## SHEET FUNCTIONS

def drawCropMarks(rows, cols, boxWidth, boxHeight, badgeWidth, badgeHeight, margin):
    # assuming we are in the top right, draw crop marks
    with savedState():
        stroke(1)
        for row in range(rows+1):
            line((-margin, -row*badgeHeight), (-margin/2, -row*badgeHeight))
            line((boxWidth+margin, -row*badgeHeight), (boxWidth+margin/2, -row*badgeHeight))
        for col in range(cols+1):
            line((col*badgeWidth, margin), (col*badgeWidth, margin/2))
            line((col*badgeWidth, -boxHeight-margin/2), (col*badgeWidth, -boxHeight-margin))

def drawSheets(data, w, h, sheetWidth=8.5*pt, sheetHeight=11*pt, badgeWidth=None, badgeHeight=None, margin=.25*pt, multiple=2):
    """
    Make a sheet of badges for printing purposes.
    """

    if not badgeWidth:
        badgeWidth = w
    if not badgeHeight:
        badgeHeight = h

    # determine available space
    boxWidth = sheetWidth - margin * 2
    boxHeight = sheetHeight - margin * 2
    # determine number of columns and rows
    cols = int ( boxWidth / badgeWidth )
    rows = int ( boxHeight / badgeHeight )

    # reset the box space based on the badge size, rather than the page size
    boxWidth = cols * badgeWidth
    boxHeight = rows * badgeHeight


    textColor = black
    nameBoxColor = white


    #setup first page
    newPage(sheetWidth, sheetHeight)
    # fill the sheet with the background color, as a rudimentary bleed
    
    rect(0, sheetHeight-boxHeight-margin-margin, sheetWidth, boxHeight+margin*2)
    # move to the top left corner, which is where we will start
    translate(margin, sheetHeight-margin)
    # draw crop marks
    drawCropMarks(rows, cols, boxWidth, boxHeight, badgeWidth, badgeHeight, margin)
    # drop down to the bottom left corner to draw the badges
    translate(0, -badgeHeight)

    # loop through data
    rowTick = 0
    colTick = 0
    for i, rowData in enumerate(data):
        firstName, lastName, company = parseRowData(rowData, colHeaders)

        bleedLeft = 100
        bleedRight = 0
        prevColor = None
        for m in range(multiple):
            # draw the badge without setting the page size
            
            if colTick == 0:
                bleedLeft = 100
                bleedRight = 0
            else:
                bleedLeft = 0
                bleedRight = 100
                
            bgColor = colorPalette['background']
            drawBadge(
                w,
                h,firstName,
                lastName,
                company,
                setSize=False,
                phase=1,
                bleedLeft=bleedLeft,
                bleedRight=bleedRight,
            )
            translate(badgeWidth, 0)
            prevColor = bgColor

            # if we have made it to the last column, translate back and start the next one
            if colTick == cols - 1:
                translate(-badgeWidth*cols, 0)
                translate(0, -badgeHeight)
                colTick = 0


                # if we have made it to the last row (and there is still more data), start a new page
                if rowTick == rows - 1 and i != len(data) - 1:
                    # setup a new page
                    newPage(sheetWidth, sheetHeight)
                    # fill the sheet with the background color, as a rudimentary bleed
                    rect(0, sheetHeight-boxHeight-margin-margin, sheetWidth, boxHeight+margin*2)
                    # move to the top left corner, which is where we will start
                    translate(margin, sheetHeight-margin)
                    # draw crop marks
                    drawCropMarks(rows, cols, boxWidth, boxHeight, badgeWidth, badgeHeight, margin)
                    # drop down to the bottom left corner to draw the badges
                    translate(0, -badgeHeight)
                    rowTick = 0
                else:
                    rowTick += 1
            else:
                colTick += 1

## READING DATA

def readDataFromCSV(csvPath):
    """
    populate a list with rows from a csv file
    """
    data = []
    headers = None
    with open(csvPath, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(csvreader):
            if i != 0:
                data.append(row)
            else:
                headers = row
            #for char in row[1]:
            #    print(char, ord(char), unicodedata.name(char))

    return headers, data


if __name__ == "__main__":

    # New DrawBot drawing state
    newDrawing() 
    # Format:
    #    "single" (single badge),
    #    "sheets" (3-up badges),
    #    "screen" (single, 1920 x 1080)
    #    "animation" (1920 x 1080) EXPERIMENTAL! GLITCHY! WATCH OUT! :)
    FORMAT = "single"

    # load data from a csv
    basePath = os.path.split(__file__)[0]

    csvPath = os.path.join(basePath, '../partial/attendees.csv')

    colHeaders, data = readDataFromCSV(csvPath)
    
    #data = data[24:25]
    #data = data[0:30]


    if FORMAT == "sheets":
        w = 4 * pt
        h = 3 * pt
        scaleValue = 5

        # let's draw some sheets.
        # Since we are not double-sided printing, we will print each twice, side-by-side,
        # and fold along the middle.
        drawSheets(data,
            w,
            h,
            sheetWidth = 8.5*pt,
            sheetHeight = 11*pt,
            badgeWidth = w,
            badgeHeight = h,
            margin = .25*pt,
            multiple=2,
            )

        os.makedirs('output', exist_ok=True)
        saveImage(os.path.join(basePath, 'output/badgebot-output-sheets.pdf'))

    elif FORMAT == "single":
        w = 4 * pt
        h = 3 * pt
        scaleValue = 5
        #random.shuffle(data)

        for i, rowData in enumerate(data):

            firstName, lastName, company = parseRowData(rowData, colHeaders)

            newPage(w*scaleValue, h*scaleValue)
            scale(scaleValue, scaleValue)

            drawBadge(
                w,
                h,
                firstName,
                lastName,
                company,
                setSize=False,
                )
            #if i > 2:
            #    break

        saveImage(os.path.join(basePath, 'output/badgebot-output-single.pdf'))

    elif FORMAT == "screen":
        w = 1920
        h = 1080
        scaleValue = (1920/w)

        for i, rowData in enumerate(data[1:]):

            firstName, lastName, company = parseRowData(rowData, colHeaders)

            newPage(1920, 1080)
            scale(scaleValue, scaleValue)

            drawBadge(
                w,
                h,
                firstName,
                lastName,
                company,
                setSize=False,
                pointSize=200
                )

        saveImage(os.path.join(basePath, 'output/badgebot-output-screen.pdf'))

    elif FORMAT == "animation":
        w = 1920
        h = 1080
        scaleValue = (1920/w)

        for i, rowData in enumerate(data[1:]):

            firstName, lastName, company = parseRowData(rowData, colHeaders)

            newDrawing()
            size(1920, 1080)

            totalFrames = 30
            for f in range(totalFrames):
                frameDuration(1/30)

                if not f == 0:
                    newPage()

                scale(scaleValue, scaleValue)

                drawBadge(
                    w,
                    h,
                    firstName,
                    lastName,
                    company,
                    setSize=False,
                    pointSize=220,
                    phase=f/totalFrames
                    )

            fullName = firstName+lastName
            saveImage(os.path.join(basePath, 'output/badgebot-output-animation-%s.gif' % fullName))

            if i > 2:
                break

print('\n\n'.join(linebreakExceptions))