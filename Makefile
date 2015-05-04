README.md: cheryl.ipynb
	ipython nbconvert cheryl.ipynb --to=markdown
	mv cheryl.md README.md

test:
	py.test --doctest-modules cheryl.py
	py.test

cov: 
	py.test --cov .

covhtml: 
	py.test --cov-report html --cov .
