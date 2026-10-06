# slopcannon-flask-db-todo

A small todo app with a Vite/React frontend and a Flask API. Each component is
built into its own arm64 OCI image with Cloud Native Buildpacks; there are no
Dockerfiles.

## Local builds

Install [`pack`](https://buildpacks.io/docs/for-platform-operators/how-to/integrate-ci/pack/).
From the repository root, run:

```sh
pack build todo-web --path frontend --platform linux/arm64 --env VITE_API_URL=http://todo-api.localhost:8088
pack build todo-api --path backend --platform linux/arm64
```

The API needs a reachable Postgres database configured with `DATABASE_URL`.
When it is unset, the API still starts and serves `/health`, while `/todos`
returns a database-not-configured response.

## GitHub packages

The Actions workflow publishes both components to GitHub Container Registry
when changes are pushed to `main` or the workflow is manually dispatched. The
first Actions run creates private packages. Set each package's visibility to
**Public** in GitHub Packages, or the cluster cannot pull the images.

The catalog refers to each image through its mutable `latest` tag. A later push
of `:latest` does not restart an already running pod, because the tag string in
the catalog does not change; restart the pod to use the new image.

The frontend's `VITE_API_URL` is inlined at build time. Set the repository
variable `VITE_API_URL` to override the default
`http://todo-api.localhost:8088` used by the workflow.
