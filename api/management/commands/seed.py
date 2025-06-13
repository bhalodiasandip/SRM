from django.core.management.base import BaseCommand
from django.db import connection
from api.models import Village, Area, Farmer, Labor, Skill, Requirement, BidComment, Bid, Tractor, TractorSkill
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group


def truncate_data():
    with connection.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE "bid_comment" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "bid" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "requirement" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "tractor_skill" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "skill" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "labor" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "farmer_areas" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "farmer_villages" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "tractor_villages" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "farmer" RESTART IDENTITY CASCADE')        
        cursor.execute('TRUNCATE TABLE "tractor" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "area" RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE "village" RESTART IDENTITY CASCADE')     
        cursor.execute('TRUNCATE TABLE "auth_group" RESTART IDENTITY CASCADE')


def create_data():
    # Villages
    v1 = Village.objects.create(village_name='ભાયાવદર')
    v2 = Village.objects.create(village_name='અરણી')
    Village.objects.create(village_name='મોટી પાનેલી')
    Village.objects.create(village_name='કોલકી')

    # Areas
    a1 = Area.objects.create(area_name='જગબીડ', village=v1, area_type='outside')
    Area.objects.create(area_name='પાનેલી ની સીમ', village=v1, area_type='outside')
    Area.objects.create(area_name='મોજીરા ની સીમ', village=v1, area_type='outside')
    a4 = Area.objects.create(area_name='છેલ', village=v1, area_type='outside')
    Area.objects.create(area_name='ખીરસરા ની સીમ', village=v2, area_type='outside')
    Area.objects.create(area_name='જાંબુડો વાડી', village=v2, area_type='outside')

    # Skills with payment type flags
    s1 = Skill.objects.create(skill_name='નીંદવું', skill_type="labor", per_day=True, lump_sump=True)
    s2 = Skill.objects.create(skill_name='કપાસ ઉપાડવો', skill_type="labor", per_day=True, lump_sump=True, per_weight=True)
    s3 = Skill.objects.create(skill_name='તલ વાઢવા', skill_type="labor", per_day=True, lump_sump=True)
    s4 = Skill.objects.create(skill_name='પાળા કરવા', skill_type="labor", per_day=True, lump_sump=True)

    m1 = Skill.objects.create(skill_name='દાંતી મારવી', skill_type="tractor", per_bigha=True, hourly=True, lump_sump=True)
    m2 = Skill.objects.create(skill_name='રોટાવેટર', skill_type="tractor", per_bigha=True, hourly=True, lump_sump=True)
    m3 = Skill.objects.create(skill_name='સમાર', skill_type="tractor", per_bigha=True, hourly=True, lump_sump=True)
    m4 = Skill.objects.create(skill_name='ઓરણી', skill_type="tractor", per_bigha=True, hourly=True, lump_sump=True)
    m5 = Skill.objects.create(skill_name='ઓટોમેટિક લેવલ', skill_type="tractor", per_bigha=True, hourly=True, lump_sump=True)

    # Users (Farmer, Labor, Tractor)
    f_user = User.objects.get(username="9510777630")
    l_user = User.objects.get(username="9784123569")
    t_user = User.objects.get(username="9428123456")

    # Farmer
    farmer = Farmer.objects.create(user=f_user, contact_number='9510777630')
    farmer.villages.set([v1])
    farmer.areas.set([a1, a4])

    # Labor
    labor = Labor.objects.create(contact_number='9784123569', user=l_user, village=v1, area=a1, gender='male', hourly_rate=300)

    # Tractor
    tractor = Tractor.objects.create(user=t_user, contact_number='9428123456')
    tractor.villages.set([v1, v2])

    # Tractor Skills
    TractorSkill.objects.create(tractor=tractor, skill=m2)  # Rotavator
    TractorSkill.objects.create(tractor=tractor, skill=m5)  # Auto Level

    # Requirements        
    req1 = Requirement.objects.create(
        title='10 વીઘા માં કપાસ ઉપાડવો',
        description='જગબીડ માં પાનેલી ની સીમ નજીક વાડી માં છેલ્લી વીણી નો કપાસ ઝડપ થી ઉપાડી શકે તેવા મજૂર ની જરૂર છે.',
        area=a1,
        skill=s2,
        farmer=farmer,
        land_size=10,
        from_date='2025-12-10',
        to_date='2025-12-20',
        shift='fullday',
        number_of_labors=10,
        has_pickup=True,
        snacks_facility=False,
        is_open=True,
        hire_labor=labor,
        farmer_rating=4.0        
    )

    req2 = Requirement.objects.create(
        title='4 વીઘા માં રોટાવેટર',
        description='છેલ ની વાડી માં રોટાવેટર મારવા નું છે.',
        area=a4,
        skill=m2,
        farmer=farmer,
        land_size=4,
        from_date='2025-04-28',
        to_date='2025-05-01',
        shift='evening',
        is_open=False,
        hire_tractor=tractor,
        farmer_rating=4.2,
        number_of_labors=0
    )

    # Bids
    Bid.objects.create(
        requirement=req1,
        labor=labor,
        description='હું 10 જણા ની ટીમ લઇ ને આવી જઈશ.',
        lump_sump=600,
        date='2025-12-15',
        male_labors=7,
        female_labors=3
    )

    Bid.objects.create(
        requirement=req2,
        tractor=tractor,
        description='આવી જઈશ રોટાવેટર લઇ ને.. કલાક ના 200.',
        hourly=200,
        date='2025-04-30'
    )


User = get_user_model()


class Command(BaseCommand):
    help = 'Truncate and seed the database'

    def handle(self, *args, **kwargs):
        truncate_data()
        User.objects.all().delete()

        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                table_name = User._meta.db_table
                pk_name = User._meta.pk.column
                seq_sql = f"SELECT pg_get_serial_sequence('{table_name}', '{pk_name}');"
                cursor.execute(seq_sql)
                seq_name = cursor.fetchone()[0]
                if seq_name:
                    cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1;")
                    self.stdout.write(self.style.WARNING(f'Reset sequence: {seq_name}'))
                else:
                    self.stdout.write(self.style.ERROR('Could not determine sequence name.'))
            else:
                self.stdout.write(self.style.WARNING('Not PostgreSQL, skipping sequence reset.'))

        self.stdout.write(self.style.WARNING('Truncated auth_user table.'))

        # Create default users
        User.objects.create_superuser(
            username='shine',
            email='info@shinecorner.com',
            password='shine12',
            first_name="admin",
            last_name="admin"
        )

        group_farmer = Group.objects.create(name='farmer')
        group_labor = Group.objects.create(name='labor')
        group_tractor = Group.objects.create(name='tractor')

        f_user = User.objects.create_user(username="9510777630", email="", password="123456", first_name="Ramesh", last_name="Bhalodiya")
        l_user = User.objects.create_user(username="9784123569", email="", password="123456", first_name="Ramji", last_name="Mooli")
        t_user = User.objects.create_user(username="9428123456", email="", password="123456", first_name="Vikram", last_name="Tractor")

        f_user.groups.add(group_farmer)
        l_user.groups.add(group_labor)
        t_user.groups.add(group_tractor)

        create_data()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
