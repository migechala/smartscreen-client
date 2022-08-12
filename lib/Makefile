CC = g++

INCLUDES = -I/opt/homebrew/Cellar/sdl2/2.0.22/include -I/opt/homebrew/Cellar/sdl2/2.0.22/include/SDL2 -I/opt/homebrew/Cellar/sdl2_ttf/2.20.0/include -I/opt/homebrew/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/include/python3.9

CXXFLAGS = -std=c++0x

LXXFLAGS = -L/opt/homebrew/lib -lSDL2 -lSDL2_ttf -ldl -D_THREAD_SAFE -framework CoreFoundation

all: main.o
	$(CC) $(INCLUDES) $(LXXFLAGS) obj/main.o -o obj/smartscreen 
	sh bash/compile_python.sh

main.o: main.cpp
	$(CC) $(INCLUDES) main.cpp -c -o obj/main.o $(CXXFLAGS)

install:
	sudo sh bash/install.sh

clean:
	rm -R obj/*