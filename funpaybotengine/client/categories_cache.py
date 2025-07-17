from __future__ import annotations


__all__ = ('CategoriesCache',)

from typing import overload
from collections.abc import Sequence

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.categories import Category, Subcategory


class CategoriesCache:
    def __init__(self, categories: Sequence[Category]):
        self._categories = categories

        self._categories_by_id: dict[int, Category] = {}
        self._categories_by_name: dict[str, Category] = {}
        self._subcategories_by_id: dict[SubcategoryType, dict[int, Subcategory]] = {
            i: {} for i in SubcategoryType
        }
        self._subcategories_to_categories_mapping: dict[
            SubcategoryType, dict[int, Category]
        ] = {i: {} for i in SubcategoryType}

        for i in categories:
            self._categories_by_id[i.id] = i
            self._categories_by_name[i.full_name] = i

            for j in i.subcategories:
                self._subcategories_by_id[j.type][j.id] = j
                self._subcategories_to_categories_mapping[j.type][j.id] = i

    def get_category_by_id(self, id: int) -> Category | None:
        return self._categories_by_id.get(id)

    def get_category_by_name(self, name: str) -> Category | None:
        return self._categories_by_name.get(name)

    def get_subcategory_by_id(
        self, type: SubcategoryType, id: int
    ) -> Subcategory | None:
        return self._subcategories_by_id[type].get(id)

    @overload
    def get_subcategory_category(
        self, type: SubcategoryType, id: int, subcategory: None = ...
    ) -> Category | None: ...

    @overload
    def get_subcategory_category(
        self, type: None = ..., id: None = ..., subcategory: Subcategory = ...
    ) -> Category | None: ...

    def get_subcategory_category(
        self,
        type: SubcategoryType | None = None,
        id: int | None = None,
        subcategory: Subcategory | None = None,
    ) -> Category | None:
        if subcategory is not None:
            return self._subcategories_to_categories_mapping[subcategory.type].get(
                subcategory.id
            )

        if type is not None and id is not None:
            return self._subcategories_to_categories_mapping[type].get(id)
        return None
