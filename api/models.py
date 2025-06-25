from django.db import models
from django.contrib.auth.models import User

# Village Model
class Village(models.Model):
    village_name = models.CharField(max_length=100)

    def __str__(self):
        return self.village_name

    class Meta:
        db_table = "village"


# Area Model
class Area(models.Model):
    AREA_CHOICES = [('inside', 'Inside'), ('outside', 'Outside')]
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    area_name = models.CharField(max_length=100)
    area_type = models.CharField(max_length=10, choices=AREA_CHOICES)

    def __str__(self):
        return f'{self.area_name} - {self.area_type}'

    class Meta:
        db_table = "area"

# Skill Model
class Skill(models.Model):
    skill_name = models.CharField(max_length=100)
    skill_type = models.CharField(
        max_length=10,
        choices=[("labor", "Labor"), ("tractor", "Tractor")],
        default="labor"
    )
    # Flags for payment types supported by this skill
    hourly = models.BooleanField(default=False)
    lump_sump = models.BooleanField(default=False)
    per_bigha = models.BooleanField(default=False)
    per_day = models.BooleanField(default=False)
    per_weight = models.BooleanField(default=False)

    def __str__(self):
        return self.skill_name

    class Meta:
        db_table = "skill"

# Farmer Model
class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15)
    villages = models.ManyToManyField(Village)
    areas = models.ManyToManyField(Area, blank=True)

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name}'

    class Meta:
        db_table = "farmer"


# Labor Model
class Labor(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name}'

    class Meta:
        db_table = "labor"


# Tractor Model (updated: removed areas)
class Tractor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15)
    villages = models.ManyToManyField(Village)
    skills = models.ManyToManyField(
        Skill,
        limit_choices_to={"skill_type": "tractor"},  # Ensures only tractor-type skills
        related_name="tractors"  # Optional: reverse relation
    )

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name}'

    class Meta:
        db_table = "tractor"


# Requirement Model
class Requirement(models.Model):
    SHIFT_CHOICES = [
        ('anytime', 'Any Time'),
        ('morning', 'Morning'),        
        ('evening', 'Evening'),        
        ('night', 'Night'),
        ('fullday', 'Full Day')        
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land_size = models.DecimalField(max_digits=10, decimal_places=2)
    from_date = models.DateField()
    to_date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    number_of_labors = models.PositiveIntegerField(null=True, blank=True)
    has_pickup = models.BooleanField(default=False)
    snacks_facility = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    hire_labor = models.ForeignKey(Labor, null=True, blank=True, on_delete=models.SET_NULL)
    hire_tractor = models.ForeignKey(Tractor, null=True, blank=True, on_delete=models.SET_NULL)
    farmer_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "requirement"

# Bid Model
class Bid(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name="bids")
    labor = models.ForeignKey(Labor, null=True, blank=True, on_delete=models.SET_NULL)
    tractor = models.ForeignKey(Tractor, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)

    # Payment amount fields (nullable) — shown as per related skill flags
    hourly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lump_sump = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    per_bigha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    per_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    date = models.DateField()

    male_labors = models.PositiveIntegerField(null=True, blank=True)
    female_labors = models.PositiveIntegerField(null=True, blank=True)
    is_accepted_by_farmer = models.BooleanField(default=False)
    is_accepted_by_labor = models.BooleanField(default=False)

    def __str__(self):
        bidder = self.labor.user.get_full_name() if self.labor else self.tractor.user.get_full_name()
        return f'Bid for {self.requirement.title} by {bidder}'

    class Meta:
        db_table = "bid"   

# Bid Comment Model
class BidComment(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    comment = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'Comment by {self.posted_by} on {self.bid}'

    class Meta:
        db_table = "bid_comment"
