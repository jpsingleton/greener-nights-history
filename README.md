# Greener Nights History

This repository automatically scrapes and archives the latest "Greener Nights" forecast from the [Octopus Energy GB API](https://api.backend.octopus.energy/v1/graphql/#query=%7B%0A%20%20greenerNightsForecast%20%7B%0A%20%20%20%20date%0A%20%20%20%20greennessScore%0A%20%20%20%20isGreenerNight%0A%20%20%20%20greennessIndex%0A%20%20%7D%0A%7D).

## What it does

- **Automated Scraping:**
  A GitHub Actions workflow (`.github/workflows/scrape.yml`) runs daily, or whenever triggered, to fetch data from the Octopus Energy Greener Nights API.
- **Data Storage:**
  The retrieved forecast data is stored (and versioned) in a JSON file (`greener-nights-history.json`) in this repository, creating an ongoing historical record.
- **Historical Tracking:**
  The workflow tracks whether each date was **ever** forecasted as a greener night (new `wasGreenerNight` property), preserving this information even if subsequent forecasts change.

## How it works

- The GitHub Actions workflow uses `curl` to POST a GraphQL query to the Octopus Energy backend API endpoint.
- The response includes forecast information such as:
  - `date`: Forecast date
  - `greennessScore`: Numeric index of how "green" the energy is
  - `isGreenerNight`: Boolean flag for greener night eligibility (current forecast)
  - `greennessIndex`: Qualitative rating (e.g. `LOW`, `MEDIUM`, `HIGH`)
  - `wasGreenerNight`: Boolean flag indicating if this date was **ever** forecasted as a greener night
- The workflow merges new data with historical data using `jq`:
  - For each date, if `isGreenerNight` was **ever** `true` in previous scrapes, `wasGreenerNight` remains `true`
  - This creates a permanent record of dates that were predicted to be greener nights, even if forecasts later change
- The data is written to `greener-nights-history.json`
- If the data changes, it is automatically committed and pushed to the repository by the workflow for versioned history.

## Historical Tracking Logic

The `wasGreenerNight` property provides insight into forecast stability:

- **First time seeing a date:** `wasGreenerNight = isGreenerNight`
- **Subsequent scrapes:** `wasGreenerNight = wasGreenerNight OR isGreenerNight`
  - Once `true`, it stays `true` forever for that date
  - `isGreenerNight` can still change based on new forecasts

### Example Scenario

**Day 1 scrape:**

```json
{
  "date": "2025-12-25",
  "isGreenerNight": true,
  "wasGreenerNight": true
}
```

**Day 2 scrape (forecast changed):**

```json
{
  "date": "2025-12-25",
  "isGreenerNight": false,
  "wasGreenerNight":  true
}
```

This shows that December 25th was **originally** predicted to be a greener night, but the forecast was later revised.

## Example data

```json
{
  "data": {
    "greenerNightsForecast": [
      {
        "date": "2025-12-23",
        "greennessScore":  52,
        "isGreenerNight": true,
        "greennessIndex": "MEDIUM",
        "wasGreenerNight": true
      },
      {
        "date": "2025-12-24",
        "greennessScore": 35,
        "isGreenerNight": false,
        "greennessIndex": "MEDIUM",
        "wasGreenerNight": true
      }
    ]
  }
}
```

## Usage

Simply visit the repository to access or download the latest historical and current forecast data from `greener-nights-history.json`.
Developers and researchers can easily pull the full change history using git.

### Use cases

- **Forecast reliability analysis:** Compare `isGreenerNight` vs `wasGreenerNight` to identify forecast changes
- **Planning decisions:** Use `wasGreenerNight` to understand if a date was ever predicted to be greener
- **Data science:** Study patterns in how forecasts evolve over time

## Why archive this?

Octopus Energy's Greener Nights forecasts are useful for tracking when cleaner overnight (23:00-06:00) energy use is encouraged.
The API responses change over time, but Octopus does not provide a public archive. This workflow builds that archive automatically in a public, auditable way, while also preserving information about forecast changes through the `wasGreenerNight` property.

---

Maintained by [@jpsingleton](https://github.com/jpsingleton)
