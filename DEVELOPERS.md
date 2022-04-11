# Notes for developers

## System requirements

### just

```sh
# macOS
brew install just

# Linux
# Install from https://github.com/casey/just/releases

# Add completion for your shell. E.g. for bash:
source <(just --completions bash)

# Show all available commands
just #  shortcut for just --list
```


## Local development environment


### Native

#### Prerequisites

- **Python v3.10.x**
- **virtualenv**
- **pip**
- **Docker (for running postgres)**

#### Setup
Set up a local development environment with:
```
just devenv
```

## Tests
Run the tests with:
```
just test <args>
```

## Run the application
```
just run
```
