# Greener Nights History

This repository automatically scrapes and archives the latest "Greener Nights" forecast from the [Octopus Energy GB API](https://api.backend.octopus.energy/v1/graphql/#query=%7B%20greenerNightsForecast%20%7B%20date%20greennessScore%20isGreenerNight%20greennessIndex%20%7D%20%7D).

## What it does

- **Automated Scraping:**  
  A GitHub Actions workflow (`.github/workflows/scrape.yml`) runs daily, or whenever triggered, to fetch data from the Octopus Energy Greener Nights API.
- **Data Storage:**  
  The retrieved forecast data is stored (and versioned) in a JSON file (`greener-nights-history.json`) in this repository, creating an ongoing historical record.

## How it works

- The GitHub Actions workflow uses `curl` to POST a GraphQL query to the Octopus Energy backend API endpoint.
- The response includes forecast information such as:
    - `date`: Forecast date
    - `greennessScore`: Numeric index of how "green" the energy is
    - `isGreenerNight`: Boolean flag for greener night eligibility
    - `greennessIndex`: Qualitative rating (e.g. `LOW`, `MEDIUM`, `HIGH`)
- The data is written to `greener-nights-history.json`
- If the data changes, it is automatically committed and pushed to the repository by the workflow for versioned history.

## Example data

```json
{
  "data": {
    "greenerNightsForecast": [
      {
        "date": "2025-12-23",
        "greennessScore": 52,
        "isGreenerNight": true,
        "greennessIndex": "MEDIUM"
      },
      ...
    ]
  }
}
```

## Usage

Simply visit the repository to access or download the latest historical and current forecast data from `greener-nights-history.json`.  
Developers and researchers can easily pull the full change history using git.

## Why archive this?

Octopus Energy’s Greener Nights forecasts are useful for tracking when cleaner overnight (23:00-06:00) energy use is encouraged.
The API responses change over time, but Octopus does not provide a public archive. This workflow builds that archive automatically in a public, auditable way.


---

Maintained by [@jpsingleton](https://github.com/jpsingleton)
