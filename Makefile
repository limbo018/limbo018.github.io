all: jemdoc cv 

cv: 
	make -C cv_yibo

jemdoc:
	make -C jemdoc
