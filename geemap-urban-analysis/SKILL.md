---
name: geemap-urban-analysis
description: Urban environmental analysis skill using Google Earth Engine and geemap. Use this skill when users ask about (1) city vegetation/greenness analysis or NDVI calculations, (2) urban expansion timelapse or city growth history visualization, (3) water body/lake/river area change monitoring or NDWI analysis. Triggers on keywords like "city green", "vegetation coverage", "NDVI", "urban expansion", "timelapse", "water area change", "NDWI", "lake shrinkage", or city environmental health assessment.
metadata:
  github_url: https://github.com/gee-community/geemap
  github_hash: 7aa37a7876ba73ab51b4fe81db6e6ec1d750f7e8
  version: 0.1.0
  created_at: 2026-01-27
---

# GeeMap Urban Analysis

Analyze urban environments using Google Earth Engine satellite data. This skill provides three core capabilities for city environmental assessment.

## Prerequisites

Ensure the following are installed and configured:
```bash
pip install geemap earthengine-api
```

Earth Engine authentication is required on first use. The scripts will prompt for authentication if needed.

## Capabilities

### 1. City Greenness Analysis (NDVI)

Analyze urban vegetation coverage using Sentinel-2 satellite data.

**When to use:** User asks about city vegetation, green space, plant coverage, or environmental health.

**Script:** `scripts/city_ndvi_analysis.py`

**Usage:**
```bash
python scripts/city_ndvi_analysis.py <city_name> [year] [output_dir]
```

**Example:**
```bash
python scripts/city_ndvi_analysis.py "Beijing" 2023 ./output
```

**Output:**
- NDVI mean value (0-1 range)
- Rating: Excellent (>0.6), Good (0.4-0.6), Fair (0.2-0.4), Poor (<0.2)
- Interactive HTML map with green-colored vegetation overlay

**Key parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| city_name | City name in English | Required |
| year | Analysis year | Current year |
| output_dir | Output directory | Current dir |

**Technical details:**
- Data source: COPERNICUS/S2_SR_HARMONIZED (Sentinel-2)
- Index: NDVI = (B8-B4)/(B8+B4) where B8=NIR, B4=Red
- Season: Summer (June-September) for best vegetation signal
- Cloud filter: <20% cloud coverage

---

### 2. Urban Expansion Timelapse

Generate animated GIF showing city growth from 1984 to present.

**When to use:** User asks about city expansion history, urban sprawl visualization, or historical development.

**Script:** `scripts/city_timelapse.py`

**Usage:**
```bash
python scripts/city_timelapse.py <city_name> [start_year] [end_year] [output_dir]
```

**Example:**
```bash
python scripts/city_timelapse.py "Las Vegas" 1984 2024 ./output
```

**Output:**
- Animated GIF showing year-by-year changes
- NIR-Red-Green false color composite (urban areas appear bright)
- Progress bar and year labels

**Key parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| city_name | City name | Required |
| start_year | Start year (min 1984) | 1984 |
| end_year | End year | Current year |
| output_dir | Output directory | Current dir |

**Technical details:**
- Data source: Landsat Collection (5/7/8/9)
- Bands: NIR-Red-Green false color for urban visibility
- Season: Summer (June-September)
- Cloud masking: Fmask applied

**Interpretation guide:**
- Bright areas = built-up urban zones
- Green areas = vegetation/farmland
- Track expansion direction by observing edge changes

---

### 3. Water Area Change Monitoring (NDWI)

Monitor changes in lakes, rivers, and reservoirs between two years.

**When to use:** User asks about water body changes, lake shrinkage, river drying, or wetland monitoring.

**Script:** `scripts/water_area_change.py`

**Usage:**
```bash
python scripts/water_area_change.py <city_name> <year1> <year2> [output_dir]
```

**Example:**
```bash
python scripts/water_area_change.py "Wuhan" 2016 2023 ./output
```

**Output:**
- Water area in km² for both years
- Change percentage (+ increase, - decrease)
- Trend assessment (Significant increase/decrease, Stable, etc.)
- Comparison map (blue=water gain, red=water loss)

**Key parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| city_name | City name | Required |
| year1 | Baseline year (min 2015) | Required |
| year2 | Comparison year | Required |
| output_dir | Output directory | Current dir |

**Technical details:**
- Data source: COPERNICUS/S2_SR_HARMONIZED (Sentinel-2)
- Index: MNDWI = (B3-B11)/(B3+B11) where B3=Green, B11=SWIR1
- Water threshold: MNDWI > 0
- Resolution: 10m per pixel

---

## Workflow

1. **Identify user intent** from their question:
   - Green/vegetation/NDVI → Use capability 1
   - Expansion/growth/timelapse → Use capability 2
   - Water/lake/river change → Use capability 3

2. **Extract parameters** from user request:
   - City name (required for all)
   - Year(s) if specified
   - Output location preference

3. **Run appropriate script** with extracted parameters

4. **Interpret results** for the user:
   - Translate numerical values to plain language
   - Explain what the visualization shows
   - Provide context (e.g., "expansion mainly toward the east")

## Common City Names

Use English names for best results:
- China: Beijing, Shanghai, Shenzhen, Guangzhou, Wuhan, Chengdu
- US: New York, Los Angeles, Las Vegas, Phoenix, Houston
- Other: Tokyo, London, Paris, Mumbai, Dubai

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication error | Run `earthengine authenticate` in terminal |
| City not found | Try more specific name or add country (e.g., "Paris, France") |
| No data for year | Sentinel-2 starts 2015, Landsat starts 1984 |
| Slow processing | Large cities take longer; consider using smaller ROI |
