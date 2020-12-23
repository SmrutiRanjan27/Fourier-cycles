import numpy as np
import matplotlib.pyplot as plt
import pygame as pg
from pygame_widgets import Slider, TextBox
import cv2
from skimage import filters

WIDTH, HEIGHT = (600, 600)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = ("#39FF14")
RED = (255,7,58)
INIT_EPC = 100

pg.init()
fps, draw_fps = 60, 100
clock = pg.time.Clock()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption('Fourier Series')
pg.mouse.set_cursor(*pg.cursors.tri_left)
#slider = Slider(screen,WIDTH-340,HEIGHT-50,170,16,min=1, max=50, step=1,color=WHITE,handleColor=BLACK,handleRadius=8,initial=INIT_EPC)
#textBox = TextBox(screen, WIDTH-140,HEIGHT-70,40,40,fontSize=15,colour=BLACK,textColour=GREEN)
font1 = pg.font.Font('freesansbold.ttf', 16)
draw_text = font1.render('DRAW SOMETHING !', True, GREEN, BLACK)
text_rect = draw_text.get_rect()
text_rect.center = [WIDTH//2,HEIGHT//2]

def fourier_coef(k,t,y):
	series = np.transpose(np.array([range(1,k+1)]*len(t)))
	t_ = np.array([t]*k)
	y_ = np.array([y]*k)
	T = (t[-1]-t[0])
	size = len(t)
	cos_ = np.cos(2*np.pi*series*t_/T)
	sin_ = np.sin(2*np.pi*series*t_/T)
	a_k = np.zeros((k,size-1))
	b_k = np.zeros((k,size-1))
	a_0 = np.zeros(size-1)
	for i in range(1,size):
		a_k[:,i-1] = (t_[:,i]-t_[:,i-1])*(y_[:,i]*cos_[:,i]+y_[:,i-1]*cos_[:,i-1])/2.
		b_k[:,i-1] = (t_[:,i]-t_[:,i-1])*(y_[:,i]*sin_[:,i]+y_[:,i-1]*sin_[:,i-1])/2.
		a_0[i-1] = y[i]*(t[i]-t[i-1])
	a = np.transpose(np.sum(a_k,axis=1)*2)/T
	b = np.transpose(np.sum(b_k,axis=1)*2)/T
	a0 = np.sum(a_0)
	return a0, a, b

def fourier_draw(a0,a,b,t,T,amp,start):
	k = len(a)
	centers, radii = [], []
	cos_= a*np.cos(2*np.pi*np.array(range(1,k+1))*t/T)
	sin_= b*np.sin(2*np.pi*np.array(range(1,k+1))*t/T)
	for i in range(k+1):
		if i == 0:
			centers.append(start)
			radii.append(amp*a0)
		else:
			centers.append(centers[i-1]+radii[i-1])
			radii.append(amp*(cos_[i-1]+sin_[i-1]))
	centers.append(centers[-1]+ radii[-1])
	return np.array(centers[-1]), centers, radii

def DrawLoop(display_text=True):
	draw_run=True
	X, Y = [], []
	while draw_run:
		screen.fill(BLACK)
		if display_text:
			screen.blit(draw_text, text_rect)
		events = pg.event.get()
		for event in events:
			if event.type == pg.QUIT:
				draw_run=False
			if event.type == pg.MOUSEBUTTONDOWN:
				display_text = False
			if event.type == pg.MOUSEBUTTONUP:
				draw_run=False
		if not display_text:
			x, y = pg.mouse.get_pos()
			X.append(x)
			Y.append(y)
		for s in range(len(X)-1):
			pg.draw.line(screen, GREEN, (X[s],Y[s]), (X[s+1],Y[s+1]),width=3)
		pg.display.update()
		clock.tick(draw_fps)
	return np.array(X)-WIDTH/2,np.array(Y)+HEIGHT/2


def Gameloop(X,Y):
	run=True
	draw_run = False
	if len(X) >200:
		val_ = 100
	else:
		val_ = 10
	time = np.linspace(0.,1.,len(X))
	a0_x, a_x, b_x = fourier_coef(val_, time, X)
	a0_y, a_y, b_y = fourier_coef(val_, time, Y)
	t_step = time[1]-time[0]
	t, T = t_step, time[-1]-time[0]
	X_, Y_ = [], []
	amp=1.
	while run:
		screen.fill(BLACK)
		events = pg.event.get()
		for event in events:
			if event.type == pg.QUIT:
				run=False
			if event.type == pg.MOUSEBUTTONDOWN:
				draw_run = True
				run = False
		x, center_x, radii_x  = fourier_draw(a0_x, a_x, b_x, t, T, amp, WIDTH/2.)
		y, center_y, radii_y = fourier_draw(a0_y, a_y, b_y, t, T, amp, HEIGHT/2.)
		radii = np.sqrt(np.array(radii_x)**2+np.array(radii_y)**2)
		X_.append(x)
		Y_.append(y)
		if t>time[-1]:
			X_, Y_ = [], []
			t = 0
		if t:
			for s in range(1,len(X_)-1):
				pg.draw.line(screen, GREEN, (X_[s],HEIGHT-Y_[s]), (X_[s+1],HEIGHT-Y_[s+1]),width=3)
		for i in range(val_+1):
			#pg.draw.circle(screen, WHITE, (center_x[i], HEIGHT-center_y[i]), radii[i], width=1)
			pg.draw.line(screen, RED, (center_x[i], HEIGHT-center_y[i]), (center_x[i+1], HEIGHT-center_y[i+1]),width=2)
		t+=t_step
		pg.display.update()
		clock.tick(fps)
	if draw_run:
		X, Y = DrawLoop(False)
		Gameloop(np.array(X),HEIGHT-np.array(Y))
	pg.quit()
	quit()

if __name__ == "__main__":
	X, Y = DrawLoop()
	Gameloop(np.array(X),HEIGHT-np.array(Y))