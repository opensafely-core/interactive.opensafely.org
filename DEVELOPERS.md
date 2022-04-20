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

### Prerequisites

- **Python v3.10.x**
- **virtualenv**
- **pip**
- **Docker** (for running postgres)
- **Node.js v16.x** ([fnm](https://github.com/Schniz/fnm#installation) is recommended for Node.js and npm)
- **npm v7.x**

### Setup

Set up a local development environment with:

```sh
just devenv
```

### Build the assets

See the [Compiling assets](#compiling-assets) section.

## Tests

Run the tests with:

```sh
just test <args>
```

## Run the application

```sh
just run
```

## Frontend development (CSS/JS)

This project uses [Vite](https://vitejs.dev/), a modern build tool and development server, to build the frontend assets.
Vite integrates into the Django project using the [django-vite](https://github.com/MrBin99/django-vite) package.

Vite works by compiling JavaScript files, and outputs a manifest file, the JavaScript files, and any included assets such as stylesheets or images.

Vite adds all JavaScript files to the page using [ES6 Module syntax](https://caniuse.com/es6-module).
For legacy browsers, this project is utilising the [Vite Legacy Plugin](https://github.com/vitejs/vite/tree/main/packages/plugin-legacy) to provide a fallback using the [module/nomodule pattern](https://philipwalton.com/articles/deploying-es2015-code-in-production-today/).

For styling this project uses [Scss](https://www.npmjs.com/package/sass) to compile the stylesheets, and then [PostCSS](https://github.com/postcss/postcss) for post-processing.

### Running the local asset server

Vite has a built-in development server which will serve the assets and reload them on save.

To run the development server:

1. Update the `.env` file to `DJANGO_VITE_DEV_MODE=True`
2. Open a new terminal and run `npm run dev`

This will start the Vite dev server at [localhost:3000](http://localhost:3000/) and inject the relevant scripts into the Django templates.

### Compiling assets

To view the compiled assets:

1. Update the `.env` file to `DJANGO_VITE_DEV_MODE=False`
2. Run `just assets-rebuild`

Vite builds the assets and outputs them to the `assets/dist` folder.

[Django Staticfiles app](https://docs.djangoproject.com/en/4.0/ref/contrib/staticfiles/) then collects the files and places them in the `staticfiles/bundle` folder, with the manifest file located at `staticfiles/bundle/manifest.json`.
