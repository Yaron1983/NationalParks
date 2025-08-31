from django.db import migrations, models


def dedupe_parks(apps, schema_editor):
    Park = apps.get_model('parks', 'Park')
    Rating = apps.get_model('parks', 'Rating')

    # Ensure no NULLs
    for p in Park.objects.all():
        if p.country is None:
            p.country = ''
        if p.region is None:
            p.region = ''
        p.save(update_fields=['country', 'region'])

    seen = {}
    for p in Park.objects.order_by('id'):
        key = (
            (p.name or '').strip().lower(),
            (p.country or '').strip().lower(),
            (p.region or '').strip().lower(),
        )
        if key in seen:
            keep = seen[key]
            # Move ratings from duplicate park p to keep, without breaking unique (park,user)
            for r in Rating.objects.filter(park=p).order_by('-created_at', '-id'):
                existing = Rating.objects.filter(park=keep, user_id=r.user_id).order_by('-created_at', '-id').first()
                if existing:
                    # Decide which rating to keep (newer wins)
                    winner = r if (r.created_at or existing.created_at) and (r.created_at >= existing.created_at) else existing
                    loser = existing if winner is r else r
                    if loser.pk == r.pk:
                        # Just drop r
                        r.delete()
                    else:
                        # Drop existing, then move r to keep
                        existing.delete()
                        r.park_id = keep.id
                        r.save(update_fields=['park'])
                else:
                    r.park_id = keep.id
                    r.save(update_fields=['park'])
            # delete duplicate park
            p.delete()
        else:
            seen[key] = p


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('parks', '0003_remove_rating_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='country',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='park',
            name='region',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(dedupe_parks, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='park',
            unique_together={('name', 'country', 'region')},
        ),
    ] 