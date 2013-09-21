SHELL=/bin/bash -e
PATH:=$(PATH):node_modules/.bin

package.json:
	npm install

npm: package.json

coffee: npm
	coffee --output static/lib --compile lib/coffeescript

setup_virtualenv: env/.setup_virtualenv

env/.setup_virtualenv: requirements.txt
	virtualenv --python=python3 env
	(unset PYTHONPATH; source env/bin/activate; pip3 install --requirement=requirements.txt)
	touch env/.setup_virtualenv

clean:
	-rm -rf env

test:
	./run_tests.sh

.PHONY: setup_virtualenv clean test npm coffee
