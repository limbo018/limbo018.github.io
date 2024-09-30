all:
	python3 ../ref/bibconvert.py --suffix cv_cn --highlight "Yibo Lin" --highlight "Lin, Yibo" --highlight "林亦波" --input ../ref/Top.bib --input ../ref/publications.bib > doc/publication.tex
	xelatex cv_yibo_cn.tex

clean:
	rm *.aux *.log *.nav *.out *.snm *.toc
