all: run

export FLASK_APP=chainletter
export FLASK_ENV=development

clean:
	rm -f instance/chainletter.sqlite

init: clean
	flask admin init-db

run:
	sqlite3 -init - -column -header instance/chainletter.sqlite 'select sha256,depth from hashchain'
	flask run

clean-run: init run
	;

test:
	pytest ./tests
