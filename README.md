# scripts
Collection of scripts for various tasks
# requirements
- docker
- make
# usage
```
cp .env.example .env
```
- Obtain FT_UID, FT_SECRET and place in .env, make sure they have sufficient permissions
- Place a csv file containing logins in app/inputs with the same name as the script
```
make
```
