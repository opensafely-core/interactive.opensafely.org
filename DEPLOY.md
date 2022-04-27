## Deployment

Deployment uses `dokku` and requires the environment variables defined in `dotenv-sample`.
It is deployed to our `dokku1` instance.


## Deployment instructions

### Create app

On dokku1, as the `dokku` user:

```sh
dokku$ dokku apps:create interactive
dokku$ dokku domains:add interactive.opensafely.org
```

### Create a postgres database
TBC

### Set up app to pull image from GitHub Container Registry

```sh
dokku$ dokku git:from-image interactive ghcr.io/opensafely-core/interactive@sha256:5b8fbad4ba6c595e292676e8d0c32920fbfa60f629ce5db92689338f0db9ef0a
```

### Configure app

```sh
# set environment variables using dotenv.sample
# For example
dokku$ dokku config:set interactive BASE_URL=https://interactive.opensafely.org
```

### Setup SSL

Requires the `letsencrypt` plugin

Note: cloudfront must be configured to redirect traffic from http to https **after** this step. Access is required via HTTP on port 80 in order for letsencrypt to perform the authenication step when setting up the SSL certificate


```sh
# Check plugins installed:
dokku$ dokku plugin:list

# enable letsencrypt
dokku$ dokku letsencrypt:enable interactive

```
