all:
	python3 ../ref/bibconvert.py --suffix cv --highlight "Yibo Lin" --highlight "Lin, Yibo" --input ../ref/Top.bib --input ../ref/publications.bib > doc/publication.tex
	xelatex cv_yibo.tex
	xelatex cv_yibo_address.tex

clean:
	rm *.aux *.log *.nav *.out *.snm *.toc
