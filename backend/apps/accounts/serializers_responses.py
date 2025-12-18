# Project modules
from apps.abstracts.serializers import SuccessResponseSerializer
from apps.accounts.serializers import UserSerializer


class UserSuccessResponseSerializer(SuccessResponseSerializer):
    data = UserSerializer()
