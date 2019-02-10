
gen: book/book.css book/book_template.html identifier/identifier_template.html \
	identifier/identifier.css
	mkdir -p gen && python gen.py

identifier_pdf:  gen
	mkdir -p pdf
	weasyprint gen/identifier.html pdf/identifier.pdf

book_pdf: gen
	mkdir -p pdf
	weasyprint gen/book.html pdf/book.pdf

book: gen book_pdf


