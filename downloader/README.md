# Downloader (Playwright Skeleton)

This folder contains **skeleton scripts** to automate CSV/QFX downloads from your institutions.
You must inspect each site's DOM once and replace the placeholder selectors.

## Setup
```bash
cd downloader
cp .env.example .env   # fill in credentials (consider a read-only account)
npm install
npm run install:pw
```

## Run
```bash
npm run download:fidelity
npm run download:boa
npm run download:usbank
npm run download:citi
# or all at once
npm run download:all
```

Downloads will save into the project `etl/downloads/...` folders, which the ETL will pick up.
