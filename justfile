set dotenv-load := true

# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

export BIN := VIRTUAL_ENV + if os_family() == "unix" { "/bin" } else { "/Scripts" }
export PIP := BIN + if os_family() == "unix" { "/python -m pip" } else { "/python.exe -m pip" }
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"

export DEFAULT_PYTHON := if os_family() == "unix" { "python3.10" } else { "python" }


# list available commands
default:
    @"{{ just_executable() }}" --list


# clean up temporary files
clean:
    rm -rf .venv $WORKSPACE_REPO


# ensure valid virtualenv
virtualenv:
    #!/usr/bin/env bash
    # allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-$DEFAULT_PYTHON}

    # create venv and upgrade pip
    test -d $VIRTUAL_ENV || { $PYTHON_VERSION -m venv $VIRTUAL_ENV && $PIP install --upgrade pip; }

    # ensure we have pip-tools so we can run pip-compile
    test -e $BIN/pip-compile || $PIP install pip-tools


_compile src dst *args: virtualenv
    #!/usr/bin/env bash
    # exit if src file is older than dst file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test "${FORCE:-}" = "true" -o {{ src }} -nt {{ dst }} || exit 0
    $BIN/pip-compile --allow-unsafe --generate-hashes --output-file={{ dst }} {{ src }} {{ args }}


# update requirements.prod.txt if requirements.prod.in has changed
requirements-prod *args:
    "{{ just_executable() }}" _compile requirements.prod.in requirements.prod.txt {{ args }}


# update requirements.dev.txt if requirements.dev.in has changed
requirements-dev *args: requirements-prod
    "{{ just_executable() }}" _compile requirements.dev.in requirements.dev.txt {{ args }}


# ensure prod requirements installed and up to date
prodenv: requirements-prod
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.prod.txt -nt $VIRTUAL_ENV/.prod || exit 0

    $PIP install -r requirements.prod.txt
    touch $VIRTUAL_ENV/.prod

# ensure dev db is running
db:
    docker-compose -f docker/docker-compose.yml up --detach db

_env:
    test -f .env || cp dotenv-sample .env

workspace-repo: _env
    #!/bin/bash
    . .env
    type=${WORKSPACE_REPO:0:4}
    test "$type" == "http" && exit
    test "$type" == "git@" && exit
    test -d "$WORKSPACE_REPO/.git" && exit
    mkdir -p $WORKSPACE_REPO
    git -C $WORKSPACE_REPO init --bare
    echo 'This is a bare local repo for testing. Use "git show $TAG" to see a commit.' > $WORKSPACE_REPO/README.md



# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# ensure dev requirements installed and up to date
devenv: _env prodenv requirements-dev && install-precommit
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.dev.txt -nt $VIRTUAL_ENV/.dev || exit 0

    $PIP install -r requirements.dev.txt
    touch $VIRTUAL_ENV/.dev


# ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install


# upgrade dev or prod dependencies (specify package to upgrade single package, all by default)
upgrade env package="": virtualenv
    #!/usr/bin/env bash
    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    FORCE=true "{{ just_executable() }}" requirements-{{ env }} $opts


# *args is variadic, 0 or more. This allows us to do `just test -k match`, for example.
# Run the tests
test *args: devenv assets-collect db
    $BIN/coverage run --module pytest {{ args }}
    $BIN/coverage report || $BIN/coverage html


# Run only tests marked as being hypothesis tests using the local profile specified in conftest
test-hypothesis *ARGS: devenv db
    $BIN/python -m pytest -m hypothesis --hypothesis-profile local {{ ARGS }}


check-migrations: devenv
    $BIN/python manage.py makemigrations --dry-run --check


# runs the format (black), sort (isort) and lint (flake8) checks but does not change any files
check: devenv
    $BIN/black --check .
    $BIN/isort --check-only --diff .
    $BIN/flake8


# fix formatting and import sort ordering
fix: devenv
    $BIN/black .
    $BIN/isort .

# Run the dev project
run *args: devenv db workspace-repo
    $BIN/python manage.py runserver {{ args }}

# Remove built assets and collected static files
assets-clean:
  rm -rf assets/dist
  rm -rf staticfiles

# Clean install the Node.js dependencies
assets-install:
  npm ci

# Build the Node.js assets
assets-build:
  npm run build

# Collect the static files
assets-collect:
  $BIN/python manage.py collectstatic --no-input

# Clean, reinstall, build and collect all assets
assets-rebuild: assets-clean assets-install assets-build assets-collect

# build docker image env=dev|prod
docker-build env="dev": _env
    {{ just_executable() }} docker/build {{ env }}

# run tests in docker container
docker-test *args="": _env
    {{ just_executable() }} docker/test {{ args }}

# run dev server in docker container
docker-serve: _env
    {{ just_executable() }} docker/serve

# run cmd in dev docker continer
docker-run *args="bash": _env
    {{ just_executable() }} docker/run {{ args }}

# exec command in an existing dev docker container
docker-exec *args="bash": _env
    {{ just_executable() }} docker/exec {{ args }}
