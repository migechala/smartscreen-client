CC = g++
INCLUDES = -I/opt/homebrew/Cellar/sdl2/2.0.22/include -I/opt/homebrew/Cellar/sdl2/2.0.22/include/SDL2 -I/opt/homebrew/Cellar/sdl2_ttf/2.20.0/include
CXXFLAGS = -std=c++0x
LXXFLAGS = -L/opt/homebrew/lib -lSDL2 -lSDL2_ttf

all: main.o
	$(CC) $(INCLUDES) $(LXXFLAGS) obj/main.o -o obj/smartscreen 

main.o: main.cpp
	$(CC) $(INCLUDES) main.cpp -c -o obj/main.o $(CXXFLAGS)

install:
	sudo ./install.sh

clean:
	rm -R obj/*