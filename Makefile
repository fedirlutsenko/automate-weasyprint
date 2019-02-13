
.PHONY: book identifier

gen/book.html: book/book.css book/book_template.html 
gen/identifier.html: /identifier_template.html identifier/identifier.css

gen:
	mkdir gen

pdf:
	mkdir pdf

gen/book.html gen/identifier.html: gen schedule.yaml data.json
	python gen.py

pdf/identifier.pdf:  gen/identifier.html pdf
	weasyprint gen/identifier.html pdf/identifier.pdf

pdf/book.pdf: gen/book.html pdf
	weasyprint gen/book.html pdf/book.pdf

book: pdf/book.pdf

identifier: pdf/identifier.pdf


