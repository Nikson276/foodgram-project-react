from typing import Optional


class RecipeCreateValidation():
    error_message: Optional[str] = None

    def run_custom_validation(self, attrs: dict) -> Optional[str]:
        """ Реализация дополнительной валидации ингредиентов и тегов"""
        if not attrs['ingredients']:
            self.error_message = "Ингредиенты не переданы"
        else:
            ingredients_list: list = []
            for ingredient in attrs['ingredients']:
                if ingredient['amount'] < 1:
                    self.error_message = (
                        f"Кол-во ингредиента {ingredient['id']} меньше 1."
                    )
                    break
                else:
                    ingredients_list.append(ingredient['id'])

            if (len(ingredients_list) > 0 and
                    len(ingredients_list) != len(set(ingredients_list))):
                self.error_message = "Ингредиенты повторяются"

        if self.error_message:
            return self.error_message

        if not attrs['tags']:
            self.error_message = "Теги не переданы"
        else:
            tags_list = [tag.id for tag in attrs['tags']]
            if len(tags_list) != len(set(tags_list)):
                self.error_message = "Теги повторяются"

        if self.error_message:
            return self.error_message
