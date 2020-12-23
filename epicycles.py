import numpy as np
import pygame as pg
from pygame_widgets import Slider, TextBox, Button

WIDTH, HEIGHT = (600, 600)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = ("#39FF14")
RED = (255,7,58)
INIT_EPC = 20

pg.init()
fps = 60
clock = pg.time.Clock()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption('Fourier Series')
pg.mouse.set_cursor(*pg.cursors.tri_left)
slider = Slider(screen,WIDTH-340,HEIGHT-50,170,16,min=1, max=50, step=1,color=WHITE,handleColor=BLACK,handleRadius=8,initial=INIT_EPC)
textBox = TextBox(screen, WIDTH-140,HEIGHT-70,40,40,fontSize=15,colour=BLACK,textColour=GREEN)
on_button = Button(screen, WIDTH-150, 20, 50, 30, text="ON",
					fontSize=15, margin=20,
		            inactiveColour=GREEN,
		            hoverColour=(128,128,128),
		            pressedColour=WHITE, radius=2,
		            onClick=lambda:True)
off_button = Button(screen, WIDTH-80, 20, 50, 30, text="OFF",
					fontSize=15, margin=20,
		            inactiveColour=RED,
		            hoverColour= (128,128,128),
		            pressedColour=WHITE, radius=2,
		            onClick=lambda:True)
font1 = pg.font.Font('freesansbold.ttf', 16)
text = font1.render('Epicycles : ', True, GREEN, BLACK)
button_text = font1.render("Circles : ", True, GREEN, BLACK)
text_rect = text.get_rect()
button_rect = button_text.get_rect()
text_rect.center = [WIDTH-420,HEIGHT-40]
button_rect.center = [WIDTH-200, 40]
X, Y = [], []
with open("data-pi.txt", "r") as file:
	for line in file.readlines():
		x, y = line.split("\t")
		X.append(np.float(x))
		Y.append(np.float(y))

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

def Gameloop(X,Y):
	run=True
	val_ = INIT_EPC
	time = np.linspace(0.,1.,len(X))
	a0_x, a_x, b_x = fourier_coef(val_, time, X)
	a0_y, a_y, b_y = fourier_coef(val_, time, Y)
	t, T = 0, time[-1]-time[0]
	t_step = time[1]-time[0]
	X_, Y_ = [], []
	amp=40
	circle_switch = False
	while run:
		screen.fill(BLACK)
		screen.blit(text, text_rect)
		screen.blit(button_text, button_rect)
		events = pg.event.get()
		for event in events:
			if event.type == pg.QUIT:
					run=False
		slider.listen(events)
		slider.draw()
		val = slider.getValue()
		textBox.setText("{:d}".format(val))
		textBox.draw()
		switch_on = on_button.listen(events)
		switch_off = off_button.listen(events)
		on_button.draw()
		off_button.draw()
		if switch_on == True:
			circle_switch = True
		if switch_off == True:
			circle_switch = False
		if val != val_:
			val_ = val
			a0_x, a_x, b_x = fourier_coef(val_, time, X)
			a0_y, a_y, b_y = fourier_coef(val_, time, Y)
			X_, Y_ = [], []
			t = 0
		x, center_x, radii_x  = fourier_draw(a0_x, a_x, b_x, t, T, amp, WIDTH/2.)
		y, center_y, radii_y = fourier_draw(a0_y, a_y, b_y, t, T, amp, HEIGHT/2.)
		radii = np.sqrt(np.array(radii_x)**2+np.array(radii_y)**2)
		X_.append(x)
		Y_.append(y)
		if t>time[-1]:
			X_.pop(0)
			Y_.pop(0)
		if t:
			for s in range(len(X_)-1):
				pg.draw.line(screen, GREEN, (X_[s],HEIGHT-Y_[s]), (X_[s+1],HEIGHT-Y_[s+1]),width=3)
		for i in range(val_+1):
			if circle_switch:
				pg.draw.circle(screen, WHITE, (center_x[i], HEIGHT-center_y[i]), radii[i], width=1)
			pg.draw.line(screen, RED, (center_x[i], HEIGHT-center_y[i]), (center_x[i+1], HEIGHT-center_y[i+1]),width=3)
		t+=t_step
		pg.display.update()
		clock.tick(fps)
	pg.quit()
	quit()

if __name__ == "__main__":
	Gameloop(X,Y)