CXX = /usr/local/bin/g++-8
CC = /usr/local/bin/gcc-8
CXXFLAGS = -Wall -Wconversion -O3 -fPIC -std=c++0x -fopenmp
MAIN = fm
FILES = common.cpp timer.cpp
SRCS = $(FILES:%.cpp=src/%.cpp)
HEADERS = $(FILES:%.cpp=src/%.h)

all: $(MAIN)

fm: src/train.cpp $(SRCS) $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ $< $(SRCS)

clean:
	rm -f $(MAIN)
