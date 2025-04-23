all: public tenure

public: 
	python3 ../ref/bibconvert.py --suffix cv_cn --highlight "Yibo Lin" --highlight "Lin, Yibo" --highlight "林亦波" --input ../ref/Top.bib --input ../ref/publications.bib > doc/publication.tex
	xelatex cv_yibo_cn.tex

tenure: 
	python3 ../ref/bibconvert.py --suffix cv_cn --highlight "Yibo Lin" --highlight "Lin, Yibo" --highlight "林亦波" --input ../ref/Top.bib --input ../ref/publications_tenure.bib > doc/publication_tenure.tex
	xelatex cv_yibo_tenure_cn.tex

clean:
	rm *.aux *.log *.nav *.out *.snm *.toc
