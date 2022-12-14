from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Fav, Ingredient, IngredientQuantity, Recipe,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers

User = get_user_model()


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return (Subscription.objects.filter(author=obj, user=request.user)
                .exists())


class MyTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class GetIngredientQuantitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            read_only=True)
    name = serializers.StringRelatedField(source='ingredient.name',
                                          read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientQuantity
        fields = ['id', 'name', 'measurement_unit', 'amount']


class AddIngredientQuantitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientQuantity
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class GetRecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = MyUserSerializer(read_only=True)
    tags = MyTagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Fav.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        items = obj.ingredients.all()
        return GetIngredientQuantitySerializer(items, many=True).data


class AddRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientQuantitySerializer(many=True, required=True)
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    author = MyUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time', 'author']

    def unique(self, data):
        check_list = []
        for d in data:
            if d in check_list:
                return False
            check_list.append(d)
        return True

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'errors': '?????????????? ??????????????????????'
            })

        if not self.unique(ingredients):
            raise serializers.ValidationError({
                'errors': '?????????????????????? ???????????? ???????? ??????????????????????'
            })

        zero_amount_ingredients = [ingredient for ingredient in ingredients
                                   if ingredient['amount'] <= 0]
        if zero_amount_ingredients:
            raise serializers.ValidationError(
                (f'?? ???????????????????????? '
                 f'{", ".join(x["name"] for x in zero_amount_ingredients)} '
                 f'???????????? ???????? ?????????????? ???????????????????? ???????????? ????????'))

        tags = data.get('tags')

        if not self.unique(tags):
            raise serializers.ValidationError('???????? ???????????? ???????? ??????????????????????')

        if data.get('cooking_time') <= 0:
            raise serializers.ValidationError('?????????? ?????????????????????????? '
                                              '???????????? ???? ??????????')

        return data

    def create_or_update(self, obj, ingredients):
        ingredients_list = [IngredientQuantity(
            ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientQuantity.objects.bulk_create(
            ingredients_list
        )
        obj.ingredients.set(ingredients_list)
        return obj

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        recipe = self.create_or_update(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)

        instance = self.create_or_update(instance, ingredients)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context=self.context).data


class ShoppingCartFavsSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ['recipe', 'user']

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe, context=self.context).data


class FollowSerializer(MyUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (MyUserSerializer.Meta.fields
                  + ['recipes', 'recipes_count', 'recipes_count'])

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = (
            self.context.get('request').query_params.get('recipes_limit')
        )
        if recipes_limit:
            return RecipeSerializer(
                obj.recipes.all()[:int(recipes_limit)], many=True).data
        else:
            return RecipeSerializer(obj.recipes.all(), many=True).data


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['user', 'author']

    def validate(self, data):
        author = data.get('author')
        user = self.context.get('request').user
        if author == user:
            raise serializers.ValidationError("???????????? ?????????????????????? "
                                              "???? ???????????? ????????")
        if Subscription.objects.filter(
                author=author, user=user).exists():
            raise serializers.ValidationError("???????????????? ?????? ????????????????????")
        return data

    def to_representation(self, instance):
        return FollowSerializer(instance.author, context=self.context).data
