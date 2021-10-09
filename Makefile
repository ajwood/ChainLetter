all: run

clean:
	echo TODO

run:
	FLASK_APP=chainletter FLASK_ENV=development flask run

test:
	pytest ./tests
