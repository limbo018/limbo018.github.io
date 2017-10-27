all: jemdoc cv 

cv: 
	make -C cv_yibo

jemdoc:
	make -C jemdoc

clean: 
	make clean -C cv_yibo
	make clean -C jemdoc
