import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, IngredientQuantity, Recipe, Tag


User = get_user_model()


def run():
    with open('./data/ingredients.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            (Ingredient.objects.
             get_or_create(name=record['name'],
                           measurement_unit=record['measurement_unit']))

    with open('./data/users.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            User.objects.get_or_create(username=record['username'],
                                       email=record['email'],
                                       first_name=record['first_name'],
                                       last_name=record['last_name'],
                                       password=record['password'])

    with open('./data/tags.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            Tag.objects.get_or_create(name=record['name'],
                                      color=record['color'],
                                      slug=record['slug'])

    with open('./data/recipes.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            author = get_object_or_404(User, id=record['author'])
            ingredient_list = [
                get_object_or_404(
                    IngredientQuantity,
                    ingredient=get_object_or_404(Ingredient, id=i['id']),
                    amount=i['amount']) for i in record['ingredients']]
            tag_list = [get_object_or_404(Tag, id=i) for i in record['tags']]
            Recipe.objects.get_or_create(name=record['name'],
                                         author=author,
                                         ingredients=ingredient_list,
                                         tags=tag_list,
                                         image=record['image'],
                                         text=record['text'],
                                         cooking_time=record['cooking_time'])
