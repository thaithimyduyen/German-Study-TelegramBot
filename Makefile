all: token.txt run
token.txt:
	cp token.example.txt token.txt
run:
	python3 main.py
install:
	pip3 install -r requirements.txt