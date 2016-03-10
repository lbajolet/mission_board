#!/usr/bin/env python

import Image
import random
import sys


def get_color(x, y, r):
    n = (pow(x, 3) + pow(y, 3)) ^ r
    return (n ^ ((n >> 8) << 8 ))


plain_image = Image.open("note.png")
im = plain_image.load()
r = random.randint(1, pow(2, 256))
print plain_image.size

enc_img = Image.new(plain_image.mode, plain_image.size)
enpix = enc_img.load()

for x in range(plain_image.size[0]):
    for y in range(plain_image.size[1]):
        t = random.randint(1, pow(2, 256)) % 250
        enpix[x,y] = t

for x in range(plain_image.size[0]):
    for y in range(plain_image.size[1]):
        if im[x,y] < 250 :
             s = get_color(x, y, r)
             enpix[x,y] = s

enc_img.save('enc' + '.png')
