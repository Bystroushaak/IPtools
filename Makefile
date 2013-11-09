.PHONY: all

all:
	git submodule init
	git submodule update --recursive

	-git submodule foreach "git stash"
	-git submodule foreach "git stash drop"
	-git submodule foreach "git checkout master"
	-git submodule foreach "git pull"