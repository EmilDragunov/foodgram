"""Сериализаторы для работы с пользователями."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from foodgram_backend.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from users.models import Subscription
from .validators import validate_username
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для базовой информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Метаданные."""

        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этого."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.subscriber.filter(subscribed_to=obj).exists()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Этот email уже зарегистрирован")]
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Это имя пользователя уже занято"),
            validate_username]
    )
    first_name = serializers.CharField(
        required=True, max_length=MAX_LENGTH_USERNAME,
    )
    last_name = serializers.CharField(
        required=True, max_length=MAX_LENGTH_USERNAME,
    )

    class Meta:
        """Метаданные."""

        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def to_representation(self, instance):
        """Представление."""
        result = super().to_representation(instance)
        result.pop('password')
        return result

    def create(self, validated_data):
        """Создает нового пользователя."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        """Метаданные."""

        model = User
        fields = ['avatar']

    def validate(self, attrs):
        """Валидация."""
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'avatar': 'Поле аватара является обязательным.'}
            )
        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных подписки."""

    email = serializers.EmailField(source='subscribed_to.email',
                                   read_only=True)
    id = serializers.IntegerField(source='subscribed_to.id', read_only=True)
    username = serializers.CharField(
        source='subscribed_to.username', read_only=True)
    first_name = serializers.CharField(
        source='subscribed_to.first_name', read_only=True)
    last_name = serializers.CharField(
        source='subscribed_to.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Метаданные."""

        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        """Получение подписки."""
        return True if obj.subscribed_to else False

    def get_recipes(self, obj):
        """Метод для получения рецептов подписанного пользователя."""
        from api.recipes.serializers import RecipeShortSerializer
        recipes = obj.subscribed_to.recipes.all()
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_avatar(self, obj):
        """Получение аватара."""
        if obj.subscribed_to.avatar:
            return obj.subscribed_to.avatar.url
        return None


class AddFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления подписок."""

    class Meta:
        """Мета данные."""

        model = None
        fields = 'subscribed_to', 'user'

    def __init__(self, *args, **kwargs):
        """Инициализация."""
        self.Meta.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

    def validate(self, data):
        """Валидация."""
        if data['user'] == data['subscribed_to']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data

    def to_representation(self, instance):
        """Возвращает сериализованные данные подписки."""
        instance.recipes_count = instance.subscribed_to.recipes.count()
        serializer = SubscriptionSerializer(instance, context=self.context)
        return serializer.data
