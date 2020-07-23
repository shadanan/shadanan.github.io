drawio := /Applications/draw.io.app/Contents/MacOS/draw.io

all: index.html *.svg

index.html: GitHubJupyter.ipynb
	jupyter nbconvert GitHubJupyter.ipynb --to slides
	mv GitHubJupyter.slides.html index.html

*.svg: *.drawio
	$(drawio) -x -f svg *.drawio
