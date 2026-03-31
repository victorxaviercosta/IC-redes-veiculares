#-------- Variables ---------

VENV = .venv

ifeq ($(OS), Windows_NT)
PYTHON = python
VENV_SCRIPTS = $(VENV)/Scripts/
VENV_PYTHON = $(VENV_SCRIPTS)python

else
PYTHON = python3
VENV_SCRIPTS = $(VENV)/bin/
VENV_PYTHON = $(VENV_SCRIPTS)python

endif

#-------- Parameters ---------
req_txt_file = requirements.txt

main_driver = experiment/main.py


#-------- OS management ---------
ifeq ($(OS), Windows_NT)
cmd_remove = del

else
cmd_remove = rm -rf

endif


.PHONY: build
.PHONY: install
.PHONY: venv
.PHONY: clean
.PHONY: rebuild
.PHONY: get-requirements

#=====[Default target]
build: venv install
	@echo 🏗️ All built.

#=====[Building targets]
venv:
	$(PYTHON) -m venv $(VENV)
	@echo 🌱 Python virtual enviroment built.

# install dependencies
install:
# 	$(VENV)/bin/pip install --upgrade pip
# 	$(VENV)/bin/pip install -r $(req_txt_file)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r $(req_txt_file)
	@echo 🧩 Dependencies istalled.

clean:
	$(cmd_remove) $(VENV)
	@echo 🧹 Cleaned.

rebuild: clean build

#=====[Running targets]
run:
	@$(PYTHON) $(main_driver) -et 100

#=====[Utilities targets]

get-requirements:
	$(VENV_PYTHON) -m pip freeze > $(req_txt_file)
	@echo 📝 Requirements written into $(req_txt_file).
