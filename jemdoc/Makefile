all:
	./jemdoc.py  -c custom.conf -o ../ index.jemdoc
	python ../ref/bibconvert.py --suffix web --highlight "Yibo Lin" --highlight "Lin, Yibo" --input ../ref/Top.bib --input ../ref/publications.bib --header publications_header.jemdoc > publications.jemdoc
	./jemdoc.py  -o ../ publications.jemdoc
	./jemdoc.py  -o ../ experience.jemdoc
	./jemdoc.py  -o ../ softwares.jemdoc

