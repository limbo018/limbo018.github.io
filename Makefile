all: ref cv 
.PHONY: ref cv

ref: 
	make -C ref

cv: ref
	make -C cv_yibo
	make -C cv_yibo_cn

clean: 
	make clean -C cv_yibo
	make clean -C ref
