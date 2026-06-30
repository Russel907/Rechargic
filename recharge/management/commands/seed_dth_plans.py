from django.core.management.base import BaseCommand
from recharge.models import DTHPlan


class Command(BaseCommand):
    help = 'Seed DTH recharge plans for all 5 operators'

    def handle(self, *args, **kwargs):
        plans = [

            # ─── TATA PLAY (TTV) ───────────────────────────────────────
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Hindi Value',
             'price': 67, 'validity': '1 Month', 'channels': '100-150', 'category': 'hindi', 'is_trending': False},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Marathi Super Value',
             'price': 83, 'validity': '1 Month', 'channels': '13', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Odia Super Value',
             'price': 95, 'validity': '1 Month', 'channels': '14', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Netflix Basic Combo',
             'price': 199, 'validity': '1 Month', 'channels': '18 + OTT', 'category': 'ott', 'is_trending': True},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Hindi Super Value',
             'price': 289, 'validity': '1 Month', 'channels': '200+', 'category': 'hindi', 'is_trending': True},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Tamil Thalaiva',
             'price': 308, 'validity': '1 Month', 'channels': None, 'category': 'regional', 'is_trending': False},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Hindi Dhamaal',
             'price': 355, 'validity': '1 Month', 'channels': '65', 'category': 'sports', 'is_trending': False},
            {'operator_code': 'TTV', 'operator_name': 'TATA Play', 'plan_name': 'Entertainment Starter Pack',
             'price': 449, 'validity': '1 Month', 'channels': '200+', 'category': 'combo', 'is_trending': False},

            # ─── AIRTEL DIGITAL TV (ATV) ───────────────────────────────
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Tamil Entertainment SD',
             'price': 218, 'validity': '1 Month', 'channels': '246', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Tamil Premium Family Kids Sports SD',
             'price': 308, 'validity': '1 Month', 'channels': '74', 'category': 'sports', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Tamil Family Kids Sports HD',
             'price': 328, 'validity': '1 Month', 'channels': '74', 'category': 'hd', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Hindi Basic HD (6 Months)',
             'price': 899, 'validity': '6 Months', 'channels': '47-187', 'category': 'hd', 'is_trending': True},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Tamil Entertainment SD (6 Months)',
             'price': 1099, 'validity': '6 Months', 'channels': '246', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Hindi Family Kids Sports SD (6 Mo)',
             'price': 1449, 'validity': '6 Months', 'channels': '98', 'category': 'combo', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Hindi Basic SD (1 Year)',
             'price': 1599, 'validity': '12 Months', 'channels': '187', 'category': 'basic', 'is_trending': False},
            {'operator_code': 'ATV', 'operator_name': 'Airtel DTH', 'plan_name': 'Hindi Premium Family Kids Sports HD',
             'price': 2949, 'validity': '6 Months', 'channels': '118', 'category': 'hd', 'is_trending': False},

            # ─── DISH TV (DTV) ─────────────────────────────────────────
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Bharat Prime Pack',
             'price': 46, 'validity': '1 Month', 'channels': '157', 'category': 'basic', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Classic Marathi',
             'price': 50, 'validity': '1 Month', 'channels': '168', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Classic Kannada HD',
             'price': 89, 'validity': '1 Month', 'channels': '210', 'category': 'hd', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Swagat HSM',
             'price': 93, 'validity': '1 Month', 'channels': '183', 'category': 'hindi', 'is_trending': True},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Premiere Kannada SD',
             'price': 102, 'validity': '1 Month', 'channels': '219', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Amar Bangla HD',
             'price': 120, 'validity': '1 Month', 'channels': '14', 'category': 'hd', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Super Family HSM',
             'price': 145, 'validity': '1 Month', 'channels': '201', 'category': 'combo', 'is_trending': False},
            {'operator_code': 'DTV', 'operator_name': 'Dish TV', 'plan_name': 'Delight HSM HD Hindi',
             'price': 244, 'validity': '1 Month', 'channels': '26', 'category': 'hd', 'is_trending': False},

            # ─── SUN DIRECT (STV) ──────────────────────────────────────
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Bengali Joy',
             'price': 164.41, 'validity': '1 Month', 'channels': '17 (Pay)', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Tamil Basic',
             'price': 211.02, 'validity': '1 Month', 'channels': '71', 'category': 'regional', 'is_trending': True},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Bengali Silver',
             'price': 223.73, 'validity': '1 Month', 'channels': '76 (Pay)', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'HD Bengali Value',
             'price': 232.20, 'validity': '1 Month', 'channels': '102', 'category': 'hd', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Tamil Gold',
             'price': 261.86, 'validity': '1 Month', 'channels': '78', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Tamil Basic (3 Months)',
             'price': 634.75, 'validity': '3 Months', 'channels': '71', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Bengali Joy (6 Months)',
             'price': 808.47, 'validity': '6 Months', 'channels': '17 (Pay)', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'STV', 'operator_name': 'Sun Direct TV', 'plan_name': 'Tamil Basic (6 Months)',
             'price': 1219.49, 'validity': '6 Months', 'channels': '71 + OTT', 'category': 'combo', 'is_trending': False},

            # ─── d2h / VIDEOCON (VTV) ──────────────────────────────────
            {'operator_code': 'VTV', 'operator_name': 'Videocon DTH (d2h)', 'plan_name': 'Bhojpuri Combo / Basic',
             'price': 55, 'validity': '1 Month', 'channels': '~60', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'VTV', 'operator_name': 'Videocon DTH (d2h)', 'plan_name': 'Value Marathi SD',
             'price': 110, 'validity': '1 Month', 'channels': '~120', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'VTV', 'operator_name': 'Videocon DTH (d2h)', 'plan_name': 'Gold HSM (Hindi)',
             'price': 160, 'validity': '1 Month', 'channels': '~180', 'category': 'hindi', 'is_trending': True},
            {'operator_code': 'VTV', 'operator_name': 'Videocon DTH (d2h)', 'plan_name': 'Diamond Telugu',
             'price': 225, 'validity': '1 Month', 'channels': '~190', 'category': 'regional', 'is_trending': False},
            {'operator_code': 'VTV', 'operator_name': 'Videocon DTH (d2h)', 'plan_name': 'Premium HSM HD',
             'price': 340, 'validity': '1 Month', 'channels': '~220', 'category': 'hd', 'is_trending': False},
        ]

        # Clear old DTH plans before re-seeding (avoid duplicates on re-run)
        DTHPlan.objects.all().delete()
        self.stdout.write('  🗑 Cleared old DTH plans')

        created_count = 0
        for p in plans:
            DTHPlan.objects.create(
                operator_code=p['operator_code'],
                operator_name=p['operator_name'],
                plan_name=p['plan_name'],
                price=p['price'],
                validity=p['validity'],
                channels=p['channels'],
                category=p['category'],
                is_active=True,
                is_trending=p['is_trending'],
            )
            created_count += 1
            self.stdout.write(f"  ✅ {p['operator_name']} - {p['plan_name']} ₹{p['price']}")

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! {created_count} DTH plans created.'))