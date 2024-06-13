from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from core.models import User

class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User 
        fields = ["id","username","first_name","last_name","email"]


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta:
        model = User 
        fields = ["id","username","password","first_name","last_name","email"]