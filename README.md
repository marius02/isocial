# iSocial

## How to run

1. clone the repo: `https://github.com/AlekseiMikhalev/isocial.git`
2. rename file `sample.env` to `.env` and add there your credentials
3. being inside root folder run in terminal `docker compose build`
4. run in terminal `docker-compose up`
5. open in browser http://0.0.0.0:8000/docs

If you get an error after you stopped docker compose and start it again, run `docker-compose down --volumes`.
Then run `docker-compose up` again.
