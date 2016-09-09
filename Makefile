all:
	./jemdoc.py  -c custom.conf -o ../ index.jemdoc
	./jemdoc.py  -o ../ publications.jemdoc
	./jemdoc.py  -o ../ experience.jemdoc
	./jemdoc.py  -o ../ softwares.jemdoc

