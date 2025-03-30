import os
from django.core.management.base import BaseCommand
from App.models import Disease

class Command(BaseCommand):
    help = 'Populates the Disease table with a comprehensive list of known diseases.'

    def handle(self, *args, **options):
        # List of common airborne diseases.
        airborne_diseases = [
            {
                "name": "COVID-19",
                "learn_link": "https://www.cdc.gov/coronavirus/2019-ncov/index.html",
            },
            {
                "name": "Influenza",
                "learn_link": "https://www.cdc.gov/flu/index.htm",
            },
            {
                "name": "Tuberculosis",
                "learn_link": "https://www.cdc.gov/tb/default.htm",
            },
            {
                "name": "Measles",
                "learn_link": "https://www.cdc.gov/measles/index.html",
            },
            {
                "name": "Common Cold",
                "learn_link": "https://www.cdc.gov/features/rhinoviruses/index.html",
            },
            {
                "name": "Chickenpox",
                "learn_link": "https://www.cdc.gov/chickenpox/index.html",
            },
            {
                "name": "SARS",
                "learn_link": "https://www.who.int/health-topics/severe-acute-respiratory-syndrome",
            },
            {
                "name": "MERS",
                "learn_link": "https://www.who.int/health-topics/middle-east-respiratory-syndrome",
            },
            {
                "name": "Pertussis",
                "learn_link": "https://www.cdc.gov/pertussis/index.html",
            },
            {
                "name": "RSV",
                "learn_link": "https://www.cdc.gov/rsv/index.html",
            },
            {
                "name": "Adenovirus Infection",
                "learn_link": "https://www.cdc.gov/adenovirus/index.html",
            },
            {
                "name": "Legionnaires' Disease",
                "learn_link": "https://www.cdc.gov/legionella/index.html",
            },
        ]
        
        # List of common physical (non-airborne) diseases.
        physical_diseases = [
            {
                "name": "Osteoarthritis",
                "learn_link": "https://www.cdc.gov/arthritis/basics/osteoarthritis.html",
            },
            {
                "name": "Rheumatoid Arthritis",
                "learn_link": "https://www.cdc.gov/arthritis/basics/rheumatoid-arthritis.html",
            },
            {
                "name": "Type 2 Diabetes",
                "learn_link": "https://www.cdc.gov/diabetes/basics/type2.html",
            },
            {
                "name": "Hypertension",
                "learn_link": "https://www.cdc.gov/bloodpressure/index.htm",
            },
            {
                "name": "Coronary Heart Disease",
                "learn_link": "https://www.cdc.gov/heartdisease/index.htm",
            },
            {
                "name": "Chronic Obstructive Pulmonary Disease (COPD)",
                "learn_link": "https://www.cdc.gov/copd/index.html",
            },
            {
                "name": "Stroke",
                "learn_link": "https://www.cdc.gov/stroke/index.htm",
            },
            {
                "name": "Chronic Kidney Disease",
                "learn_link": "https://www.cdc.gov/kidneydisease/index.html",
            },
            {
                "name": "Alzheimer's Disease",
                "learn_link": "https://www.cdc.gov/aging/aginginfo/alzheimers.htm",
            },
            {
                "name": "Osteoporosis",
                "learn_link": "https://www.cdc.gov/nutrition/resources-publications/osteoporosis.html",
            },
            {
                "name": "Breast Cancer",
                "learn_link": "https://www.cdc.gov/cancer/breast/",
            },
            {
                "name": "Lung Cancer",
                "learn_link": "https://www.cdc.gov/cancer/lung/",
            },
            {
                "name": "Appendicitis",
                "learn_link": "https://www.cdc.gov/appendicitis/index.html",
            },
            {
                "name": "Gallstones",
                "learn_link": "https://www.cdc.gov/nutrition/resources-publications/gallstones.html",
            },
            {
                "name": "Migraine",
                "learn_link": "https://www.cdc.gov/headaches/migraine/index.htm",
            },
            {
                "name": "Back Pain",
                "learn_link": "https://www.cdc.gov/arthritis/basics/back-pain.html",
            },
        ]

        count_created = 0
        count_updated = 0

        # Insert or update airborne diseases.
        for d in airborne_diseases:
            disease, created = Disease.objects.update_or_create(
                name=d["name"],
                defaults={
                    "disease_type": Disease.AIR,
                    "learn_link": d["learn_link"]
                }
            )
            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f"Created airborne disease: {d['name']}"))
            else:
                count_updated += 1
                self.stdout.write(self.style.WARNING(f"Updated airborne disease: {d['name']}"))
        
        # Insert or update physical diseases.
        for d in physical_diseases:
            disease, created = Disease.objects.update_or_create(
                name=d["name"],
                defaults={
                    "disease_type": Disease.PHYSICAL,
                    "learn_link": d["learn_link"]
                }
            )
            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f"Created physical disease: {d['name']}"))
            else:
                count_updated += 1
                self.stdout.write(self.style.WARNING(f"Updated physical disease: {d['name']}"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed diseases: {count_created} created, {count_updated} updated."
        ))
