all: 
	python bibconvert.py --suffix jekyll --highlight "Yibo Lin" --highlight "Lin, Yibo" --input Top.bib --input publications.bib > ../_pages/publications.md
	python bibconvert.py --suffix cvjekyll --highlight "Yibo Lin" --highlight "Lin, Yibo" --input Top.bib --input publications.bib > ../_includes/publications_cv.md
	python bibconvert.py --suffix shortref --input Top.bib --input publications.bib > ../cv_yibo/doc/publication_shortref.tex
