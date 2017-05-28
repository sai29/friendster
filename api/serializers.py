from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, ConnectionRequest

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], first_name=validated_data["first_name"], last_name=validated_data["last_name"],
        			 email=validated_data['email'], password=validated_data['password'], gender=validated_data['gender'])
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'gender')



class ConnectionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConnectionRequest
        fields = ('id','from_user','to_user', 'added_on')
