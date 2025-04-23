all: public tenure

public:
	python3 ../ref/bibconvert.py --suffix cv --highlight "Yibo Lin" --highlight "Lin, Yibo" --input ../ref/Top.bib --input ../ref/publications.bib > doc/publication.tex
	xelatex cv_yibo.tex
	xelatex cv_yibo_address.tex

tenure: 
	python3 ../ref/bibconvert.py --suffix cv --highlight "Yibo Lin" --highlight "Lin, Yibo" --input ../ref/Top.bib --input ../ref/publications_tenure.bib > doc/publication_tenure.tex
	xelatex cv_yibo_tenure.tex

repr: 
	xelatex repr_pub_list.tex

clean:
	rm *.aux *.log *.nav *.out *.snm *.toc
