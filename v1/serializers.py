from rest_framework import serializers

from users.models import User, Notice, Match
from dockerapi.models import Image, Container, Checked, Category, Hints


class ImagesSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    top_user = serializers.SerializerMethodField()
    hints = serializers.SerializerMethodField()

    def get_category(self, obj: Image):
        return obj.category.name

    def get_hints(self, obj: Image):
        return Hints.objects.filter(image=obj, status=True).values("id", "content")

    def get_top_user(self, obj: Image):
        sl = ", "
        return sl.join([user.first_name if user.first_name else user.username for user in obj.top_user.all()])

    class Meta:
        model = Image
        fields = ['id', 'check_flag', 'file', 'name', 'source', 'description', 'point', 'category',
                  'done_count', 'top_user', 'hints']


class ContainerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_image(self, obj: Container):
        return {
            "name": obj.image.name,
            "id": obj.image.id
        }

    def get_user(self, obj: Container):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }

    class Meta:
        model = Container
        fields = ['id', 'container_id', 'name', 'public_port', 'image', 'user', 'create_time']
        depth = 1


class CheckedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj: Checked):
        return {
            "id":  obj.image.id,
            "name": obj.image.name,
            "category": {
                "id": obj.image.category.id,
                "name": obj.image.category.name,
            },
        }

    def get_user(self, obj: Checked):

        return {
            "username": obj.user.username,
            "first_name": obj.user.first_name,
        }

    class Meta:
        model = Checked
        fields = ['id', 'image', 'user', 'ctimer']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'is_superuser']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'content', 'ctimer']


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'name', 'logo', 'start_datetime', 'end_datetime']


class UserCheckedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj: Checked):
        return {
            "id": obj.image.id,
            "name": obj.image.name,
            "point": obj.image.point,
            "category": obj.image.category.name,
            "check_flag": obj.image.check_flag,
            "create_time": obj.image.create_time
        }

    def get_user(self, obj: Checked):

        return {
            "username": obj.user.username,
            "first_name": obj.user.first_name,
        }

    class Meta:
        model = Checked
        fields = ['id', 'image', 'user', 'create_time']


