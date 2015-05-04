test:
	py.test --doctest-modules cheryl.py
	py.test

cov: 
	py.test --cov .

covhtml: 
	py.test --cov-report html --cov .
