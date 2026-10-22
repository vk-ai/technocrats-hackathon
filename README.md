
## Configuration and security

Settings are read from the environment (see `.env.example`):
`DJANGO_SECRET_KEY` (required unless `DJANGO_DEBUG=true`), `DJANGO_DEBUG` (default false),
`DJANGO_ALLOWED_HOSTS` (comma-separated, default `localhost,127.0.0.1`), `FCM_SERVER_KEY` (optional).

The sales-rep login returns a signed `token`; send it as `Authorization: Token <token>` to the
customer/order/sales-rep detail APIs and logout. Register, login and list-offers stay public.
Keys that were committed in earlier history must be rotated and never reused.
