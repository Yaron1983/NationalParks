import os
import json
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.apps import apps

WD_SPARQL = """
SELECT ?item ?itemLabel ?itemDescription ?image ?countryLabel ?countryCode ?adminLabel WHERE {
  ?item wdt:P31 wd:Q46169.
  OPTIONAL { ?item wdt:P18 ?image }
  OPTIONAL { ?item wdt:P17 ?country .
             ?country wdt:P297 ?countryCode }
  OPTIONAL { ?item wdt:P131 ?admin . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 500
"""

SPARQL_HEADERS = {
    'Accept': 'application/sparql-results+json',
    'User-Agent': 'NationalParksImporter/1.0 (https://example.com; contact@example.com)'
}

IMG_HEADERS = {
    'User-Agent': 'NationalParksImporter/1.0 (https://example.com; contact@example.com)'
}

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
CACHE_FILE = "parks_wiki_cache.json"
FLAGS_DIR = "media/flags/"

os.makedirs(FLAGS_DIR, exist_ok=True)


class Command(BaseCommand):
    help = "Import national parks from Wikidata, enhance with Wikipedia, and download country flags"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=300)

    def load_cache(self):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self, cache):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    def fetch_wikipedia_summary(self, park_name):
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{park_name.replace(' ', '_')}"
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return {
                "description": data.get("extract", ""),
                "official_website": data.get("content_urls", {}).get("desktop", {}).get("page")
            }
        except Exception:
            return {"description": None, "official_website": None}

    def download_flag(self, country_code):
        country_code = country_code.lower()
        flag_path = os.path.join(FLAGS_DIR, f"{country_code}.png")
        if os.path.exists(flag_path):
            return flag_path
        try:
            url = f"https://flagcdn.com/w40/{country_code}.png"
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            with open(flag_path, "wb") as f:
                f.write(resp.content)
            return flag_path
        except Exception:
            return None

    def handle(self, *args, **opts):
        global country_code
        Park = apps.get_model('parks', 'Park')
        ParkIdentifier = apps.get_model('parks', 'ParkIdentifier')
        limit = int(opts['limit'])

        cache = self.load_cache()
        query = WD_SPARQL.replace('LIMIT 500', f'LIMIT {limit}')
        url = 'https://query.wikidata.org/sparql'

        r = requests.get(url, params={'query': query}, headers=SPARQL_HEADERS, timeout=40)
        r.raise_for_status()
        results = r.json().get('results', {}).get('bindings', [])

        created_count = 0
        images_downloaded = 0
        flags_downloaded = 0

        for row in results:
            wikidata_uri = row.get('item', {}).get('value', '')
            wikidata_id = wikidata_uri.split('/')[-1] if wikidata_uri else None
            if not wikidata_id:
                continue

            identifier = ParkIdentifier.objects.filter(
                source_name='wikidata', source_id=wikidata_id
            ).first()

            if identifier:
                park = identifier.park
                self.stdout.write(f"Found existing park: {park.name}")
            else:
                name = row.get('itemLabel', {}).get('value', '')
                description = row.get('itemDescription', {}).get('value', '')
                country = (row.get('countryLabel', {}) or {}).get('value', '')
                country_code = (row.get('countryCode', {}) or {}).get('value', '')
                region = (row.get('adminLabel', {}) or {}).get('value', '')
                location = ''

                park = Park.objects.create(
                    name=name,
                    description=description,
                    country=country,
                    region=region,
                    location=location
                )

                ParkIdentifier.objects.create(
                    park=park,
                    source_name='wikidata',
                    source_id=wikidata_id
                )
                created_count += 1
                self.stdout.write(f"Created park: {park.name}")

            if not park.image:
                image_val = row.get('image', {}).get('value')
                if image_val:
                    try:
                        ext = os.path.splitext(image_val.split('?')[0])[1].lower()
                        if ext not in ALLOWED_EXTENSIONS:
                            self.stdout.write(self.style.WARNING(
                                f"Skipped image for {park.name} (unsupported format: {ext})"
                            ))
                            continue

                        img_resp = requests.get(image_val, headers=IMG_HEADERS, timeout=40)
                        img_resp.raise_for_status()
                        filename = f"{park.id}{ext}"
                        park.image.save(filename, ContentFile(img_resp.content), save=True)
                        images_downloaded += 1
                        self.stdout.write(f"Downloaded image for {park.name}")

                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"Failed to download image for {park.name}: {e}"
                        ))

            if country_code:
                flag_path = self.download_flag(country_code)
                relative_path = flag_path
                if flag_path:
                    if flag_path.startswith("media/"):
                        relative_path = flag_path[len("media/"):]
                    print(f"Downloaded image for {park.name}: {flag_path}")

                    park.flag.name = relative_path
                    park.save()
                    flags_downloaded += 1

            cache_key = park.name
            if cache_key in cache:
                wiki_data = cache[cache_key]
                self.stdout.write(f"Using cached Wikipedia data for {park.name}")
            else:
                wiki_data = self.fetch_wikipedia_summary(park.name)
                cache[cache_key] = wiki_data
                self.save_cache(cache)

            if wiki_data.get("description"):
                park.description = wiki_data["description"]
            if wiki_data.get("official_website"):
                park.official_website = wiki_data["official_website"]
            park.save()

        self.stdout.write(self.style.SUCCESS(
            f"Imported/updated {len(results)} items, created {created_count}, "
            f"downloaded {images_downloaded} images, "
            f"downloaded {flags_downloaded} flags."
        ))
