# OUTPOST AI — deployment notes (Render + MySQL)

## Render MySQL service

1. Fork or use the `render-examples/mysql` repository template from Render's official MySQL deployment guide.
2. In Render, create a **Private Service** from that repository and choose Docker.
3. Add environment variables: `MYSQL_DATABASE=outpost_ai`, `MYSQL_USER=outpost`, `MYSQL_PASSWORD=<strong-password>`, and `MYSQL_ROOT_PASSWORD=<different-strong-password>`.
4. Add a persistent disk with mount path `/var/lib/mysql` (required by the MySQL image). Render's MySQL guide uses a 10 GB disk.
5. Deploy and note the private hostname Render displays, such as `mysql-example:3306`.

## Render Flask web service

1. Push this project to GitHub. If the repository contains the outer `outpost_ai/` directory, set Render's Root Directory to `outpost_ai`. If you put the project files directly in the repository root, leave Root Directory blank.
2. In Render, choose **New → Web Service**, connect the repository, and choose Python.
3. Build command: `pip install -r requirements.txt`
4. Start command: `flask --app app init-db && flask --app app seed && gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add `OUTPOST_DATABASE_URL` with this format, replacing the values with your actual private MySQL details:

   `mysql+pymysql://outpost:YOUR_PASSWORD@MYSQL_PRIVATE_HOST:3306/outpost_ai?charset=utf8mb4`

6. Add `SECRET_KEY` with a long, randomly generated value. Do not commit either secret to GitHub.

The `init-db` command only creates missing tables. The seed command inserts demo data only when the database has no users; it does not drop or overwrite an existing database. The configuration also accepts `DATABASE_URL` and converts a `mysql://` URL to the PyMySQL driver format.

## Demo accounts

- Client: `alex@outpost.ai` / `password`
- Job provider: `jordan@outpost.ai` / `password`

These are public demo credentials. Use them only for demonstration; do not store private information in this database. Change or remove them before any real public use.
