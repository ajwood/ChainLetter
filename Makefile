all: run

export FLASK_APP=chainletter
export FLASK_ENV=development

clean:
	rm -f instance/chainletter.sqlite

init: clean
	FLASK_APP=chainletter FLASK_ENV=development flask admin init-db

run:
	sqlite3 -init /dev/null instance/chainletter.sqlite 'select sha256 from hashchain'
	flask run

clean-run: init run
	;

test:
	pytest ./tests
