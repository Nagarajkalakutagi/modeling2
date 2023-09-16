from rest_framework.serializers import ModelSerializer

from rest.models import Users


class AddUserSerializers(ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
