all: token.txt words.json install run
token.txt:
	cp token.example.txt token.txt
words.json:
	cp words.example.json words.json
run:
	python3 main.py
install:
	pip3 install -r requirements.txt