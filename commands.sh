docker volume create postgres_vol_1


docker run --rm -d \
    --name postgres_1 \
    -e POSTGRES_PASSWORD=postgres_admin \
    -e POSTGRES_USER=postgres_admin \
    -e POSTGRES_DB=test_app \
    -p 5432:5432 \
    -v postgres_vol_1:/var/lib/postgresql/data \
    --net=app_net \
    postgres