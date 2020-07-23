drawio := /Applications/draw.io.app/Contents/MacOS/draw.io

DRAWIO_FILES = $(wildcard *.drawio)
SVG_FILES = $(patsubst %.drawio, %.svg, $(DRAWIO_FILES))

all: index.html svgs

clean:
	rm -f *.svg
	rm -f index.html

index.html: GitHubJupyter.ipynb
	jupyter nbconvert GitHubJupyter.ipynb --to slides
	mv GitHubJupyter.slides.html index.html

svgs: $(SVG_FILES)

%.svg: %.drawio
	$(drawio) -x -f svg $<

variables:
	@echo DRAWIO_FILES: $(DRAWIO_FILES)
	@echo SVG_FILES: $(SVG_FILES)
