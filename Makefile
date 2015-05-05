README.md: cheryl.ipynb travis_build_status_link
	ipython nbconvert cheryl.ipynb --to=markdown
	head -n 2 cheryl.md > header
	sed '1d;2d;3d' cheryl.md > body 
	cat header travis_build_status_link body > README.md
	rm cheryl.md header body

test:
	py.test --doctest-modules cheryl.py
	py.test

cov: 
	py.test --cov .

covhtml: 
	py.test --cov-report html --cov .
