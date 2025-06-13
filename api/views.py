from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import *
from .serializers import *
from .permissions import IsFarmer, IsLabor, IsTractor
from .permissions import user_in_group


# ----------------------------
# Requirement ViewSet
# ----------------------------

class RequirementViewSet(viewsets.ModelViewSet):
    queryset = Requirement.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFarmer()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        def parse_csv(param):
            return [v.strip() for v in param.split(",") if v.strip()]

        skill_ids = self.request.query_params.get("skill_ids")
        area_ids = self.request.query_params.get("area_ids")
        payment_types = self.request.query_params.get("payment_types")
        shifts = self.request.query_params.get("shifts")
        has_pickup = self.request.query_params.get("has_pickup")
        snacks_facility = self.request.query_params.get("snacks_facility")
        min_rating = self.request.query_params.get("min_rating")
        date_str = self.request.query_params.get("date")

        if skill_ids:
            queryset = queryset.filter(skill_id__in=[int(i) for i in parse_csv(skill_ids)])

        if area_ids:
            queryset = queryset.filter(area_id__in=[int(i) for i in parse_csv(area_ids)])

        if payment_types:
            queryset = queryset.filter(payment_type__in=parse_csv(payment_types))

        if shifts:
            queryset = queryset.filter(shift__in=parse_csv(shifts))

        if has_pickup is not None:
            queryset = queryset.filter(has_pickup=(has_pickup.lower() == 'true'))

        if snacks_facility is not None:
            queryset = queryset.filter(snacks_facility=(snacks_facility.lower() == 'true'))

        if min_rating:
            try:
                min_rating_value = float(min_rating)
                if min_rating_value > 0:
                    queryset = queryset.filter(farmer_rating__gte=min_rating_value)
            except ValueError:
                pass  # optionally handle invalid float

        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(from_date__lte=date_obj, to_date__gte=date_obj)
            except ValueError:
                pass

        if user_in_group(user, 'farmer') and hasattr(user, 'farmer'):
            queryset = queryset.filter(farmer=user.farmer)

        elif user_in_group(user, 'labor') and hasattr(user, 'labor'):
            queryset = queryset.filter(
                is_open=True,
                area__village=user.labor.village,
                skill__skill_type='labor'
            ).exclude(
                bids__labor=user.labor
            )

        elif user_in_group(user, 'tractor') and hasattr(user, 'tractor'):
            queryset = queryset.filter(
                is_open=True,
                area__village__in=user.tractor.villages.values_list('id', flat=True),
                skill__skill_type='tractor'
            ).exclude(
                bids__tractor=user.tractor
            )

        else:
            queryset = queryset.none()

        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RequirementSerializer

        if self.action in ['create', 'update', 'partial_update']:
            req_type = self.request.data.get('type')
            if req_type == 'tractor':
                return TractorRequirementCreateSerializer
            elif req_type == 'labor':
                return LaborRequirementCreateSerializer
            else:
                raise serializers.ValidationError({"type": "This field is required and must be 'labor' or 'tractor'."})

        return RequirementSerializer

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user.farmer)

    def update(self, request, *args, **kwargs):
        return self._safe_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._safe_update(request, *args, **kwargs)

    def _safe_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.is_open:
            return Response({"detail": "Cannot update a closed requirement."}, status=status.HTTP_400_BAD_REQUEST)

        if Bid.objects.filter(requirement=instance).exists():
            return Response({"detail": "Cannot update a requirement that already has bids."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)


# ----------------------------
# My Requirement List View
# ----------------------------

class MyRequirementListView(ListAPIView):
    serializer_class = RequirementSerializer

    def get_permissions(self):
        user = self.request.user

        if user_in_group(user, 'farmer'):
            return [IsFarmer()]
        elif user_in_group(user, 'labor'):
            return [IsLabor()]
        elif user_in_group(user, 'tractor'):
            return [IsTractor()]
        return []

    def get_queryset(self):
        user = self.request.user

        if user_in_group(user, 'farmer') and hasattr(user, 'farmer'):
            return Requirement.objects.filter(farmer=user.farmer)

        return Requirement.objects.none()


# ----------------------------
# User Profile View
# ----------------------------

class UserProfileView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# ----------------------------
# Token Login View
# ----------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ----------------------------
# Registration View
# ----------------------------

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# Village ViewSet
# ----------------------------

class VillageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Village.objects.all()
    serializer_class = VillageSerializer
    permission_classes = [AllowAny]


# ----------------------------
# Skill ViewSet
# ----------------------------

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Skill.objects.all()
        skill_type = self.request.query_params.get("skill_type")
        if skill_type in ["labor", "tractor"]:
            queryset = queryset.filter(skill_type=skill_type)
        return queryset


# ----------------------------
# Area ViewSet
# ----------------------------

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AreaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        village_id = self.request.query_params.get('village_id')
        if village_id:
            return Area.objects.filter(village_id=village_id)
        return Area.objects.none()


# ----------------------------
# Bid ViewSet
# ----------------------------

class BidViewSet(viewsets.ModelViewSet):
    serializer_class = BidSerializer
    permission_classes = [IsLabor | IsTractor]

    def get_queryset(self):
        if user_in_group(self.request.user, 'labor') and hasattr(self.request.user, 'labor'):
            return Bid.objects.filter(labor=self.request.user.labor)
        elif user_in_group(self.request.user, 'tractor') and hasattr(self.request.user, 'tractor'):
            return Bid.objects.filter(tractor=self.request.user.tractor)
        return Bid.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user_in_group(user, 'labor') and hasattr(user, 'labor'):
            serializer.save(labor=user.labor)
        elif user_in_group(user, 'tractor') and hasattr(user, 'tractor'):
            serializer.save(tractor=user.tractor)
