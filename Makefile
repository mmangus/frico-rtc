SOURCE_FILES := src/frico_rtc/*.py tests/*.py
BLUE := \033[1;34m
GREEN := \033[1;32m
NOCOLOR := \033[0m
FRAME_TOP := ┏━┅┉
FRAME_BOTTOM := ┗━┅┉
STEP_TOP := @echo "$(BLUE)$(FRAME_TOP)$(NOCOLOR)"
STEP_BOTTOM := @echo "$(BLUE)$(FRAME_BOTTOM)$(NOCOLOR)"
SUCCESS := @echo "$(GREEN)$(FRAME_TOP)\n┋ All tests complete: success! \n$(FRAME_BOTTOM)$(NOCOLOR)"

# this project uses dependencies to skip redundant steps, but make aliases
# don't work as expected when used as dependencies, so assign vars :|
venv=.venv/bin/activate
install=.venv/.install
hooks=.venv/.hooks
piptools=.venv/.piptools
format=.venv/.format
lint=.venv/.lint
formatcheck=.venv/.format-check
typecheck=.venv/.typecheck
unit=.venv/.unit
test=.venv/.test
testci=.venv/.testci
publish=.venv/.publish

all: $(hooks) $(install)

# TODO: make step styling less repetitive
$(venv):
	$(STEP_TOP)
	@echo "$(BLUE)┋ Creating venv...$(NOCOLOR)"
	@python3 -m venv .venv
	@echo "$(GREEN)Installed virtual environment: .venv$(NOCOLOR)"
	$(STEP_BOTTOM)

$(hooks): $(venv)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Configuring git hooks...$(NOCOLOR)"
	@git config core.hooksPath git-hooks
	@touch $(hooks)
	$(STEP_BOTTOM)

$(piptools): $(venv)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Installing pip-tools...$(NOCOLOR)"
	@.venv/bin/python3 -m pip install pip-tools
	@touch $(piptools)
	$(STEP_BOTTOM)

requirements: requirements.txt $(install)

requirements.txt: requirements.in $(piptools) setup.cfg
	$(STEP_TOP)
	@echo "$(BLUE)┋ Compiling pinned dependencies...$(NOCOLOR)"
	@CUSTOM_COMPILE_COMMAND="make requirements" .venv/bin/pip-compile requirements.in
	@rm -f $(install)
	$(STEP_BOTTOM)

$(install): $(piptools)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Installing requirements...$(NOCOLOR)"
	@.venv/bin/pip-sync
	@touch $(install)
	$(STEP_BOTTOM)

$(format): $(install) $(SOURCE_FILES)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Formatting...$(NOCOLOR)"
	@echo "isort `.venv/bin/isort --version-number)`"
	@.venv/bin/isort $(SOURCE_FILES)
	@.venv/bin/black --version
	@.venv/bin/black $(SOURCE_FILES)
	@touch $(format)
	$(STEP_BOTTOM)

# for CI use, bail out of anything needs to be reformatted
$(formatcheck): $(install) $(SOURCE_FILES)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Checking format...$(NOCOLOR)"
	@echo "isort `.venv/bin/isort --version-number)`"
	@.venv/bin/isort --diff $(SOURCE_FILES)
	@.venv/bin/isort --check-only $(SOURCE_FILES)
	@.venv/bin/black --version
	@.venv/bin/black --check $(SOURCE_FILES)
	@touch $(formatcheck)
	$(STEP_BOTTOM)

$(lint): $(install) $(SOURCE_FILES)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Linting...$(NOCOLOR)"
	@echo "flake8 `.venv/bin/flake8 --version)`"
	@.venv/bin/flake8 $(SOURCE_FILES)
	@echo "$(GREEN)No complaints."
	@touch $(lint)
	$(STEP_BOTTOM)

$(typecheck): $(install) $(SOURCE_FILES)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Type checking...$(NOCOLOR)"
	@.venv/bin/mypy --version
	@.venv/bin/mypy $(SOURCE_FILES)
	@touch $(typecheck)
	$(STEP_BOTTOM)

$(unit): $(install) $(SOURCE_FILES)
	$(STEP_TOP)
	@echo "$(BLUE)┋ Running unit and doc tests...$(NOCOLOR)"
	@.venv/bin/pytest
	@touch $(unit)
	$(STEP_BOTTOM)

.PHONY: success
success:
	$(SUCCESS)

$(test): $(format) $(lint) $(typecheck) $(unit) success
	@touch $(test)

test: $(test)

$(testci): $(formatcheck) $(lint) $(typecheck) $(unit)
	@touch $(testci)

test-ci: $(testci)

dist: $(testci) $(SOURCE_FILES) README.md setup.cfg
	$(STEP_TOP)
	@echo "$(BLUE)┋ Building package...$(NOCOLOR)"
	@.venv/bin/python3 -m build
	$(STEP_BOTTOM)

package: dist

$(publish): dist
	$(STEP_TOP)
	@git diff --exit-code || (echo "Commit all changes before publishing"; exit 1)
	@echo "$(BLUE)┋ Publishing...$(NOCOLOR)"
	@python3 -m twine upload dist/*
	@touch $(publish)
	$(STEP_BOTTOM)

publish: $(publish)

.PHONY: clean
clean:
	$(STEP_TOP)
	@echo "$(BLUE)┋ Starting fresh...$(NOCOLOR)"
	@echo "Removing .venv..."
	@rm -rf .venv
	@echo "Removing packaging directories..."
	@rm -rf build
	@rm -rf dist
	@rm -rf src/frico-rtc.egg-info
	@echo "Removing test cache..."
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	$(STEP_BOTTOM)
