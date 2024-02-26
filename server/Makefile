LAMBDA_NAME=ak-check-in
UAT_LAMBDA_NAME=$(LAMBDA_NAME)-uat
PROD_LAMBDA_NAME=$(LAMBDA_NAME)-prod
FILENAME=$(LAMBDA_NAME).zip
AWSCLI=awscliv2
AWS_LAMBDA=$(AWSCLI) lambda
PYTHON_VERSION:=$(shell python --version | cut -d. -f1,2)
EXPECTED_VERSION=Python 3.12


.PHONY: install build test deploy test-remote clean all

install:
ifeq ($(PYTHON_VERSION), $(EXPECTED_VERSION))
	pip install -r requirements.txt --target build/ --upgrade
else
	@echo Incorrect python version. Expecting $(EXPECTED_VERSION)
endif

build:
	cp ak_user.py settings.py lambda_function.py test.py kms_utils.py cal_event.py build

test: build
	@cd build && \
	PYTHONPATH=. python test.py $(AUTH_HEADER)

deploy: build
	cd build && \
	zip -r $(FILENAME) * && \
	aws lambda update-function-code \
		--function-name $(UAT_LAMBDA_NAME) \
		--zip-file fileb://$(FILENAME)

deploy-prod: build
	cd build && \
	zip -r $(FILENAME) * && \
	aws lambda update-function-code \
		--function-name $(PROD_LAMBDA_NAME) \
		--zip-file fileb://$(FILENAME)

clean:
	rm -rf build

all: clean install build test deploy test-remote
