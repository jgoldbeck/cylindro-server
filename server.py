import os
import tornado.ioloop
from tornado.web import asynchronous, RequestHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.escape import json_encode, json_decode, squeeze

from urllib import urlencode
import random
import math
# from numpy import median


try: # in case spidev not connected
    spidev  = file('/dev/spidev0.0', "wb")
    spi_connected = True
except:
    print 'SPIDEV not connected'
    spi_connected = False

nleds = 240
nzeros = 15

blank = bytearray(3)
blank[0] = 128
blank[1] = 128
blank[2] = 128
zeros = bytearray(nzeros)
buff = bytearray(nleds*3)
for i in range(nleds):
    buff[3*i] = 128
    buff[3*i+1] = 128
    buff[3*i+2] = 128

buffer_black_next = False

def make_buff_black():
    global buff
    for i in range(nleds):
        buff[3*i] = 128
        buff[3*i+1] = 128
        buff[3*i+2] = 128

def make_buff_white():
    global buff
    for i in range(nleds):
        buff[3*i] = 128 + 126 # g
        buff[3*i+1] = 128 + 126 # r
        buff[3*i+2] = 128 + 126 # b

# waiting state
b = 80
r = 80
g = 80
goingUp = True
waiting = False
current_loudness = 0
current_pitches = [0] * 12

#
analyzing = False

shift_amt = 1
shift_shift_amt = 1

effect = 'camera'

# ring = int(math.floor(randomPixel / 24))
# ringPitchAmt = current_pitches[ring]
# if (ringPitchAmt > random.random()):


def addRandomPixels(n=10):
    global buff
    for x in range(n):
        randomPixel = random.randint(0, nleds)
        buff[3*randomPixel] = 128 + g
        buff[3*randomPixel+1] = 128 + r
        buff[3*randomPixel+2] = 128 + b

def shiftPixels(n=1):
    n %= 26
    global buff
    buff = buff[-3 * n :] + buff[:-3 * n]

def setRandomRGB():
    global r
    global g
    global b
    r = random.randint(0, 100) + 26
    g = random.randint(0, 100) + 26
    b = random.randint(0, 100) + 26


class IndexHandler(RequestHandler):
    def get(self):
        self.write("This is your response")
        # self.finish()

class BeeHandler(RequestHandler):
    def get(self):
        global r
        self.write("Boom boom boom")
        r = random.randint(0, 127)

class FaviconHandler(RequestHandler):
    def get(self):
        self.finish()


### begin real stuff

class AnalysisHandler(RequestHandler): # set the global analysis object
    def post(self):
        global analysis
        global analyzing
        print 'Analysis received'
        self.write('Analysis')
        analyzing = True
        # analysis = json_decode(self.request.body)
        # print 'Analysis processed'
        # analyzing = False

class SectionsNowHandler(RequestHandler):
    def post(self):
        global buff
        global shift_amt
        global buffer_black_next
        global shift_shift_amt

        self.write('New section')
        if (effect is 'camera'):
            shift_shift_amt = 1
            make_buff_white()
            buffer_black_next = True
        print 'Section'



class SectionsFutureHandler(RequestHandler):
    def post(self):
        global buff
        global shift_shift_amt
        print 'FutureSection'
        shift_shift_amt = 5
        self.write('Future section')


class BarsNowHandler(RequestHandler):
    def post(self):
        global buff
        global shift_amt
        shift_amt += shift_shift_amt

        setRandomRGB()



class BeatsNowHandler(RequestHandler):
    def post(self):
        global buff

        # if (effect is 'camera'):
        #     for x in range(3):
        #         randomPixel = random.randint(0, nleds)
        #         buff[3*randomPixel] = 128 + g
        #         buff[3*randomPixel+1] = 128 + r
        #         buff[3*randomPixel+2] = 128 + b
        numPix = int(current_loudness * 20)
        addRandomPixels(numPix)
        self.write('Beat')


class SegmentsNowHandler(RequestHandler):
    def post(self):
        global current_loudness
        global current_pitches
        body= json_decode(self.request.body)

        current_loudness = body['loudness']
        current_pitches = body['pitches']



class TatumsNowHandler(RequestHandler):
    def post(self): # change to post
        if (effect is 'camera'):
            shiftPixels(shift_amt)

        self.write('Tatum')




def main_loop():
    global buff

    if( not analyzing ):
        if (waiting):
            global b
            global goingUp


            #### waiting effect ####
            g = 8

            if (b >= 50):
                goingUp = False
            elif (b <= 0):
                goingUp = True

            if (goingUp):
                b += 1
            else:
                b -= 1

            for i in range(nleds):
                buff[3*i] = 128+g
                buff[3*i+1] = 128+r
                buff[3*i+2] = 128+b




        ### write out to leds ####

        if (spi_connected):
            spidev.write(buff+zeros)
            spidev.flush()

        global buffer_black_next
        if (buffer_black_next):
            make_buff_black()
            buffer_black_next = False



application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/bee', BeeHandler),
    (r'/beats/now', BeatsNowHandler),
    (r'/tatums/now', TatumsNowHandler),
    (r'/segments/now', SegmentsNowHandler),
    (r'/bars/now', BarsNowHandler),
    (r'/sections/now', SectionsNowHandler),
    (r'/sections/future', SectionsFutureHandler),

    (r'/analysis', AnalysisHandler),

    (r'/favicon.ico', FaviconHandler)
])

if __name__ == '__main__':
    application.listen(os.environ.get('PORT', 5000))
    io_loop = tornado.ioloop.IOLoop.instance()
    periodic = tornado.ioloop.PeriodicCallback(main_loop, 30, io_loop)
    periodic.start()
    io_loop.start()

