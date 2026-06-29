from django.core.management.base import BaseCommand
from recharge.models import Operator, Circle, Plan


class Command(BaseCommand):
    help = 'Seed operators, circles, and sample plans for mobile recharge'

    def handle(self, *args, **kwargs):
        self.stdout.write('--- Seeding Operators ---')
        self.seed_operators()

        self.stdout.write('\n--- Seeding Circles ---')
        self.seed_circles()

        self.stdout.write('\n--- Seeding Plans ---')
        self.seed_plans()

        self.stdout.write(self.style.SUCCESS('\n✅ All done!'))

    def seed_operators(self):
        operators = [
            {
                "name": "Jio",
                "code": "JIO",
                "logo": "https://res.cloudinary.com/dusncgt6b/image/upload/v1782726746/jio-logo-icon_dx9vm0.png",
            },
            {
                "name": "Airtel",
                "code": "AT",
                "logo": "https://res.cloudinary.com/dusncgt6b/image/upload/v1782726746/airtel-logo-icon_ly4oa4.png",
            },
            {
                "name": "Vi (Vodafone Idea)",
                "code": "VI",
                "logo": "https://res.cloudinary.com/dusncgt6b/image/upload/v1782726746/vi-mobile-icon_vagbcz.png",
            },
            {
                "name": "BSNL",
                "code": "BT",
                "logo": "https://res.cloudinary.com/dusncgt6b/image/upload/v1782726746/bsnl-logo-icon_qawbbm.png",
            },
        ]

        for op in operators:
            obj, created = Operator.objects.get_or_create(
                code=op["code"],
                defaults={
                    "name": op["name"],
                    "logo": op["logo"],
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created: {op['name']}")
            else:
                # Update logo even if operator exists
                obj.logo = op["logo"]
                obj.name = op["name"]
                obj.save()
                self.stdout.write(f"  🔄 Updated logo: {op['name']}")

    def seed_circles(self):
        circles = [
            {"name": "All India",                       "code": "ALL"},
            {"name": "Andhra Pradesh & Telangana",      "code": "AP"},
            {"name": "Assam",                           "code": "AS"},
            {"name": "Bihar & Jharkhand",               "code": "BH"},
            {"name": "Chennai",                         "code": "CH"},
            {"name": "Delhi & NCR",                     "code": "DL"},
            {"name": "Gujarat",                         "code": "GJ"},
            {"name": "Haryana",                         "code": "HR"},
            {"name": "Himachal Pradesh",                "code": "HP"},
            {"name": "Jammu & Kashmir",                 "code": "JK"},
            {"name": "Karnataka",                       "code": "KA"},
            {"name": "Kerala",                          "code": "KL"},
            {"name": "Kolkata",                         "code": "KO"},
            {"name": "Madhya Pradesh & Chhattisgarh",  "code": "MP"},
            {"name": "Maharashtra & Goa",               "code": "MH"},
            {"name": "Mumbai",                          "code": "MU"},
            {"name": "North East",                      "code": "NE"},
            {"name": "Odisha",                          "code": "OD"},
            {"name": "Punjab",                          "code": "PB"},
            {"name": "Rajasthan",                       "code": "RJ"},
            {"name": "Tamil Nadu",                      "code": "TN"},
            {"name": "UP East",                         "code": "UE"},
            {"name": "UP West",                         "code": "UW"},
            {"name": "West Bengal",                     "code": "WB"},
            {"name": "Uttarakhand",                     "code": "UK"},
        ]

        for c in circles:
            obj, created = Circle.objects.get_or_create(
                code=c["code"],
                defaults={"name": c["name"], "is_active": True}
            )
            if created:
                self.stdout.write(f"  ✅ Created: {c['name']}")
            else:
                self.stdout.write(f"  ⏭ Already exists: {c['name']}")

    def seed_plans(self):
        try:
            jio    = Operator.objects.get(code='JIO')
            airtel = Operator.objects.get(code='AT')
            vi     = Operator.objects.get(code='VI')
            bsnl   = Operator.objects.get(code='BT')
        except Operator.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Operator missing: {e}'))
            return

        all_india = Circle.objects.get(code='ALL')

        plans = [

            # ─── JIO 2026 ──────────────────────────────────────────────
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'recommended',
                'price': 19, 'validity': '1 Day',
                'data': '1GB', 'calls': 'No Voice',
                'includes': 'Data Add-on Booster',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 198, 'validity': '14 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema, True 5G',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 155, 'validity': '28 Days',
                'data': '2GB Total', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema (SIM Saver)',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 299, 'validity': '28 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema, JioCloud',
                'is_trending': True, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 349, 'validity': '28 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema, True Unlimited 5G',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 579, 'validity': '56 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 666, 'validity': '70 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'JioTV, JioCinema',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 899, 'validity': '90 Days',
                'data': '2GB/Day + 20GB Extra', 'calls': 'Unlimited',
                'includes': 'JioCinema, JioTV, Unlimited 5G',
                'is_trending': False, 'is_best_value': True,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 111, 'validity': '28 Days',
                'data': '5GB Total', 'calls': 'No Voice',
                'includes': 'Standalone Data Pack',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': jio, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 101, 'validity': 'Existing Plan',
                'data': 'Unlimited 5G', 'calls': 'No Voice',
                'includes': 'Works if base plan has 1.5GB/day',
                'is_trending': False, 'is_best_value': False,
            },

            # ─── AIRTEL 2026 ───────────────────────────────────────────
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 199, 'validity': '28 Days',
                'data': '2GB Total', 'calls': 'Unlimited',
                'includes': 'Wynk Music, Hellotunes (SIM Saver)',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 299, 'validity': '28 Days',
                'data': '1GB/Day', 'calls': 'Unlimited',
                'includes': 'Wynk Music',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 349, 'validity': '28 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'Apple Music, Adobe Express Premium',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 379, 'validity': '28 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'Google One 30GB, Unlimited 5G',
                'is_trending': True, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'entertainment',
                'price': 838, 'validity': '56 Days',
                'data': '3GB/Day', 'calls': 'Unlimited',
                'includes': 'Amazon Prime, SonyLIV, Unlimited 5G',
                'is_trending': False, 'is_best_value': True,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 979, 'validity': '84 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'SonyLIV, Unlimited 5G',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 22, 'validity': '1 Day',
                'data': '1GB Total', 'calls': 'No Voice',
                'includes': 'Instant Data Booster',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 26, 'validity': '1 Day',
                'data': '1.5GB Total', 'calls': 'No Voice',
                'includes': 'Instant Data Booster',
                'is_trending': False, 'is_best_value': False,
            },

            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 33, 'validity': '1 Day',
                'data': '2GB Total', 'calls': 'No Voice',
                'includes': 'Instant Data Booster',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 161, 'validity': '30 Days',
                'data': '12GB Total', 'calls': 'No Voice',
                'includes': 'Work From Home Add-on',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': airtel, 'circle': all_india,
                'plan_type': 'international',
                'price': 3599, 'validity': '365 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'Unlimited 5G, Airtel Xstream',
                'is_trending': False, 'is_best_value': False,
            },

            # ─── VI 2026 ───────────────────────────────────────────────
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 99, 'validity': '15 Days',
                'data': 'Basic Talktime Only', 'calls': 'Local Tariff',
                'includes': 'SIM Life Extension',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 199, 'validity': '28 Days',
                'data': '2GB Total', 'calls': 'Unlimited',
                'includes': 'Vi Movies & TV Basic',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 299, 'validity': '28 Days',
                'data': '1GB/Day', 'calls': 'Unlimited',
                'includes': 'Vi Movies & TV',
                'is_trending': True, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 398, 'validity': '28 Days',
                'data': 'Unlimited 5G & 4G', 'calls': 'Unlimited',
                'includes': 'No daily cap on data',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 799, 'validity': '77 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'Unlimited 5G, Weekend Data Rollover',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 859, 'validity': '84 Days',
                'data': '1.5GB/Day', 'calls': 'Unlimited',
                'includes': 'Vi Movies & TV, Weekend Rollover',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 979, 'validity': '84 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'Midnight Unlimited, SonyLIV',
                'is_trending': False, 'is_best_value': True,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'entertainment',
                'price': 1599, 'validity': '84 Days',
                'data': 'Unlimited 5G & 4G', 'calls': 'Unlimited',
                'includes': 'Netflix Basic Included',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 139, 'validity': '28 Days',
                'data': '12GB Total', 'calls': 'No Voice',
                'includes': 'Standalone Data Only',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': vi, 'circle': all_india,
                'plan_type': 'international',
                'price': 3599, 'validity': '365 Days',
                'data': '2GB/Day', 'calls': 'Unlimited',
                'includes': 'Unlimited 5G, Weekend Rollover',
                'is_trending': False, 'is_best_value': False,
            },

            # ─── BSNL 2026 ─────────────────────────────────────────────
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'recommended',
                'price': 107, 'validity': '22 Days',
                'data': '3GB Total', 'calls': '200 Mins',
                'includes': 'Cheapest plan for OTPs & banking',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 118, 'validity': '20 Days',
                'data': '10GB Total', 'calls': 'Unlimited',
                'includes': 'Light emergency usage',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 199, 'validity': '30 Days',
                'data': '2GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Standard everyday use',
                'is_trending': True, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 299, 'validity': '30 Days',
                'data': '3GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'High data/streaming package',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'talktime',
                'price': 319, 'validity': '60 Days',
                'data': '10GB Total', 'calls': 'Unlimited + 300 SMS',
                'includes': 'Secondary calling SIM',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 347, 'validity': '50 Days',
                'data': '2.5GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Balanced validity & daily quota',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 485, 'validity': '72 Days',
                'data': '2.5GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'High-value mid-range alternative',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 599, 'validity': '70 Days',
                'data': '3GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Work from home/heavy data users',
                'is_trending': False, 'is_best_value': True,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 997, 'validity': '150 Days',
                'data': '2GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': '5 months zero-worry usage',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'data_only',
                'price': 1499, 'validity': '300 Days',
                'data': '32GB Total', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Best value yearly pack to keep SIM alive',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'international',
                'price': 2399, 'validity': '365 Days',
                'data': '2GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Full year high-speed usage',
                'is_trending': False, 'is_best_value': False,
            },
            {
                'operator': bsnl, 'circle': all_india,
                'plan_type': 'unlimited_data',
                'price': 2799, 'validity': '365 Days',
                'data': '3GB/Day', 'calls': 'Unlimited + 100 SMS/Day',
                'includes': 'Maximum data plan available',
                'is_trending': False, 'is_best_value': False,
            },
        ]

        # First delete old plans to avoid duplicates from previous seed
        Plan.objects.filter(circle=all_india).delete()
        self.stdout.write('  🗑 Cleared old plans')

        created_count = 0
        for p in plans:
            Plan.objects.create(
                operator=p['operator'],
                circle=p['circle'],
                plan_type=p['plan_type'],
                price=p['price'],
                validity=p['validity'],
                data=p['data'],
                calls=p['calls'],
                includes=p['includes'],
                is_active=True,
                is_trending=p['is_trending'],
                is_best_value=p['is_best_value'],
            )
            created_count += 1
            self.stdout.write(
                f"  ✅ {p['operator'].name} ₹{p['price']} {p['validity']}"
            )

        self.stdout.write(f'\n  Total created: {created_count} plans')