import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, IngredientQuantity, Recipe, Tag

# python3 manage.py runscript scripts.{file_name} without .py
User = get_user_model()


def run():
    with open('../data/ingredients.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            (Ingredient.objects.
             get_or_create(name=record['name'],
                           measurement_unit=record['measurement_unit']))

    with open('../data/users.json') as fhand:
        data = json.load(fhand)

        users = User.objects.all()
        if not users:
            for record in data:
                print(record)
                User(username=record['username'],
                     email=record['email'],
                     first_name=record['first_name'],
                     last_name=record['last_name'],
                     password=record['password']).save()

    with open('../data/tags.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            Tag.objects.get_or_create(name=record['name'],
                                      color=record['color'],
                                      slug=record['slug'])

    with open('../data/recipes.json') as fhand:
        data = json.load(fhand)

        for record in data:
            print(record)
            author = get_object_or_404(User, id=data['author'])
            ingredient_list = [
                get_object_or_404(
                    IngredientQuantity,
                    ingredient=get_object_or_404(Ingredient, id=i['id']),
                    amount=i['amount']) for i in data['ingredients']]
            tag_list = [get_object_or_404(Tag, id=i) for i in data['tags']]
            Recipe.objects.get_or_create(name=record['name'],
                                         author=author,
                                         ingredients=ingredient_list,
                                         tags=tag_list,
                                         image=data['image'],
                                         text=data['text'],
                                         cooking_time=data['cooking_time'])
