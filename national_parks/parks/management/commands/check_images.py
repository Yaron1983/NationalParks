from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Check which parks have images and which don't"

    def add_arguments(self, parser):
        parser.add_argument('--missing-only', action='store_true', help='Show only parks without images')

    def handle(self, *args, **opts):
        Park = apps.get_model('parks', 'Park')
        parks_with_images = Park.objects.filter(image__isnull=False).exclude(image='')
        parks_without_images = Park.objects.filter(image__isnull=True) | Park.objects.filter(image='')
        
        total_parks = Park.objects.count()
        
        self.stdout.write(f"Total parks: {total_parks}")
        self.stdout.write(f"Parks with images: {parks_with_images.count()}")
        self.stdout.write(f"Parks without images: {parks_without_images.count()}")
        
        if not opts['missing_only']:
            self.stdout.write("\nParks with images:")
            for park in parks_with_images[:10]:  # Show first 10
                self.stdout.write(f"  ✓ {park.name} ({park.country})")
            if parks_with_images.count() > 10:
                self.stdout.write(f"  ... and {parks_with_images.count() - 10} more")
        
        self.stdout.write("\nParks without images:")
        for park in parks_without_images[:10]:  # Show first 10
            self.stdout.write(f"  ✗ {park.name} ({park.country})")
        if parks_without_images.count() > 10:
            self.stdout.write(f"  ... and {parks_without_images.count() - 10} more")
        
        if parks_without_images.count() > 0:
            self.stdout.write(self.style.WARNING(f"\n{parks_without_images.count()} parks need images!"))
        else:
            self.stdout.write(self.style.SUCCESS("\nAll parks have images!")) 