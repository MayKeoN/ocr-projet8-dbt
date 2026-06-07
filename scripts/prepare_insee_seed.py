import argparse
import csv
import os
import sys
from collections import defaultdict

try:
    import xlrd
except ImportError:
    print("ERROR: xlrd not installed. Run: pip install xlrd")
    sys.exit(1)

"""
prepare_insee_seed.py
---------------------
Converts the raw INSEE XLS population estimates into a clean dbt seed file.

Input : data/estim-pop-dep-sexe-aq.xls  (in .gitignore)
Output: seeds/insee_population.csv

Steps:
  1. Load INSEE XLS (estimations par département, sexe, âge quinquennal)
  2. Filter to metropolitan French regions matching OCR student regions
  3. Aggregate from département to région level
  4. Pivot to long format: one row per year x region x age_group x gender
  5. Filter to years 2022-2023 (available and relevant)
  6. Write to seeds/insee_population.csv

Run before dbtf seed when the INSEE source file has been updated.
Source: https://www.insee.fr/fr/statistiques/1893198
"""

# ---------------------------------------------------------------------------
# Department → Region mapping (current French regions as of 2016 reform)
# ---------------------------------------------------------------------------
DEP_TO_REGION = {
    '01': 'Auvergne-Rhône-Alpes',
    '03': 'Auvergne-Rhône-Alpes',
    '07': 'Auvergne-Rhône-Alpes',
    '15': 'Auvergne-Rhône-Alpes',
    '26': 'Auvergne-Rhône-Alpes',
    '38': 'Auvergne-Rhône-Alpes',
    '42': 'Auvergne-Rhône-Alpes',
    '43': 'Auvergne-Rhône-Alpes',
    '63': 'Auvergne-Rhône-Alpes',
    '69': 'Auvergne-Rhône-Alpes',
    '73': 'Auvergne-Rhône-Alpes',
    '74': 'Auvergne-Rhône-Alpes',
    '21': 'Bourgogne-Franche-Comté',
    '25': 'Bourgogne-Franche-Comté',
    '39': 'Bourgogne-Franche-Comté',
    '58': 'Bourgogne-Franche-Comté',
    '70': 'Bourgogne-Franche-Comté',
    '71': 'Bourgogne-Franche-Comté',
    '89': 'Bourgogne-Franche-Comté',
    '90': 'Bourgogne-Franche-Comté',
    '22': 'Bretagne',
    '29': 'Bretagne',
    '35': 'Bretagne',
    '56': 'Bretagne',
    '18': 'Centre-Val de Loire',
    '28': 'Centre-Val de Loire',
    '36': 'Centre-Val de Loire',
    '37': 'Centre-Val de Loire',
    '41': 'Centre-Val de Loire',
    '45': 'Centre-Val de Loire',
    '2A': 'Corse',
    '2B': 'Corse',
    '08': 'Grand Est',
    '10': 'Grand Est',
    '51': 'Grand Est',
    '52': 'Grand Est',
    '54': 'Grand Est',
    '55': 'Grand Est',
    '57': 'Grand Est',
    '67': 'Grand Est',
    '68': 'Grand Est',
    '88': 'Grand Est',
    '02': 'Hauts-de-France',
    '59': 'Hauts-de-France',
    '60': 'Hauts-de-France',
    '62': 'Hauts-de-France',
    '80': 'Hauts-de-France',
    '75': 'Île-de-France',
    '77': 'Île-de-France',
    '78': 'Île-de-France',
    '91': 'Île-de-France',
    '92': 'Île-de-France',
    '93': 'Île-de-France',
    '94': 'Île-de-France',
    '95': 'Île-de-France',
    '14': 'Normandie',
    '27': 'Normandie',
    '50': 'Normandie',
    '61': 'Normandie',
    '76': 'Normandie',
    '16': 'Nouvelle-Aquitaine',
    '17': 'Nouvelle-Aquitaine',
    '19': 'Nouvelle-Aquitaine',
    '23': 'Nouvelle-Aquitaine',
    '24': 'Nouvelle-Aquitaine',
    '33': 'Nouvelle-Aquitaine',
    '40': 'Nouvelle-Aquitaine',
    '47': 'Nouvelle-Aquitaine',
    '64': 'Nouvelle-Aquitaine',
    '79': 'Nouvelle-Aquitaine',
    '86': 'Nouvelle-Aquitaine',
    '87': 'Nouvelle-Aquitaine',
    '09': 'Occitanie',
    '11': 'Occitanie',
    '12': 'Occitanie',
    '30': 'Occitanie',
    '31': 'Occitanie',
    '32': 'Occitanie',
    '34': 'Occitanie',
    '46': 'Occitanie',
    '48': 'Occitanie',
    '65': 'Occitanie',
    '66': 'Occitanie',
    '81': 'Occitanie',
    '82': 'Occitanie',
    '44': 'Pays de la Loire',
    '49': 'Pays de la Loire',
    '53': 'Pays de la Loire',
    '72': 'Pays de la Loire',
    '85': 'Pays de la Loire',
    '04': "Provence-Alpes-Côte d'Azur",
    '05': "Provence-Alpes-Côte d'Azur",
    '06': "Provence-Alpes-Côte d'Azur",
    '13': "Provence-Alpes-Côte d'Azur",
    '83': "Provence-Alpes-Côte d'Azur",
    '84': "Provence-Alpes-Côte d'Azur",
}

# ---------------------------------------------------------------------------
# Age group mapping
# Within each gender section (Hommes/Femmes), columns are offset from base:
#   base+4  = 20-24 ans
#   base+5  = 25-29 ans
#   ...
#   base+11 = 55-59 ans
#   base+12 to base+20 = 60+ (summed)
# Hommes base col = 23, Femmes base col = 44
# ---------------------------------------------------------------------------
AGE_OFFSETS = {
    4:  '20-24 ans',
    5:  '25-29 ans',
    6:  '30-34 ans',
    7:  '35-39 ans',
    8:  '40-44 ans',
    9:  '45-49 ans',
    10: '50-54 ans',
    11: '55-59 ans',
}
AGE_60PLUS_OFFSETS = range(12, 21)  # cols 12-20 within gender section = 60+
AGE_60PLUS_LABEL = '60 ans ou plus'

GENDER_SECTIONS = [
    ('M', 23),  # Hommes section base column
    ('F', 44),  # Femmes section base column
]


def extract_year(wb, year_str):
    """Extract and aggregate population data for a single year sheet."""
    if year_str not in wb.sheet_names():
        print(f"  WARNING: Sheet '{year_str}' not found in workbook, skipping.")
        return {}

    sh = wb.sheet_by_name(year_str)
    aggregated = defaultdict(int)

    for r in range(5, sh.nrows):
        raw_code = str(sh.cell_value(r, 0)).strip()
        dep_code = raw_code.replace('.0', '').zfill(2)

        if dep_code not in DEP_TO_REGION:
            continue

        region = DEP_TO_REGION[dep_code]

        for gender, base_col in GENDER_SECTIONS:
            # Standard age groups
            for offset, age_label in AGE_OFFSETS.items():
                col = base_col + offset
                try:
                    pop = int(float(sh.cell_value(r, col)))
                except (ValueError, IndexError):
                    pop = 0
                aggregated[(region, age_label, gender)] += pop

            # 60+ group = sum of remaining age cols
            pop_60plus = 0
            for offset in AGE_60PLUS_OFFSETS:
                col = base_col + offset
                try:
                    pop_60plus += int(float(sh.cell_value(r, col)))
                except (ValueError, IndexError):
                    pass
            aggregated[(region, AGE_60PLUS_LABEL, gender)] += pop_60plus

    return aggregated


def main():
    parser = argparse.ArgumentParser(description='Prepare INSEE population seed CSV for dbt')
    parser.add_argument(
        '--input',
        default=os.path.join('data', 'estim-pop-dep-sexe-aq.xls'),
        help='Path to the INSEE XLS file (default: data/estim-pop-dep-sexe-aq.xls)'
    )
    parser.add_argument(
        '--output',
        default=os.path.join('seeds', 'insee_population.csv'),
        help='Output CSV path (default: seeds/insee_population.csv)'
    )
    parser.add_argument(
        '--years',
        nargs='+',
        default=['2022', '2023'],
        help='Years to extract (default: 2022 2023)'
    )
    args = parser.parse_args()

    # Resolve paths relative to project root (script is in scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_path = os.path.join(project_root, args.input) if not os.path.isabs(args.input) else args.input
    output_path = os.path.join(project_root, args.output) if not os.path.isabs(args.output) else args.output

    print(f"Reading: {input_path}")
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found at {input_path}")
        print(f"Place the INSEE XLS file there and retry.")
        sys.exit(1)

    wb = xlrd.open_workbook(input_path)
    print(f"Available year sheets: {[s for s in wb.sheet_names() if s.isdigit()]}")

    all_rows = []
    for year in args.years:
        print(f"Processing year {year}...")
        data = extract_year(wb, year)
        for (region, age_group, gender), population in data.items():
            all_rows.append({
                'year': int(year),
                'region': region,
                'age_group': age_group,
                'gender': gender,
                'population': population,
            })

    all_rows.sort(key=lambda r: (r['year'], r['region'], r['age_group'], r['gender']))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['year', 'region', 'age_group', 'gender', 'population'])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Written {len(all_rows)} rows to {output_path}")
    print("Done. Run 'dbtf seed' to load into Snowflake.")


if __name__ == '__main__':
    main()