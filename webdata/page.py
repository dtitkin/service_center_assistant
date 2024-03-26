
from utils.app_type import (
    PageResult,
    BackofficeData,
    Table,
    Locator,
    Products_category,
    Decimal)

from .locators import (
    LoginPage_locators,
    BackofficePage_locators,
    NewOrderPage_locators,
    WarehouseSelectionPage_locators)

from .helpers import click_all_next_button, get_table_data

from utils.task_service import TaskType


def click():
    return True


class _BasePage():
    result_all_page: PageResult = PageResult()

    def __init__(self, driver):
        self.driver = driver

        self._next_handler = None

    def set_next(self, next_hendler):
        self._next_handler = next_hendler
        return next_hendler

    def handle(self, request: list[TaskType]) -> PageResult:
        if self._next_handler:
            return self._next_handler.handle(request)

        return self.result_all_page


class _BaseElement():
    def __init__(self, locator: Locator, name_attribite=None):
        self.locator = locator
        self.name_attribite = name_attribite

    def __set__(self, obj, value):
        obj.driver.find_element(*self.locator).send_keys(value)

    def __get__(self, obj, owner):
        if not self.name_attribite:
            return obj.driver.find_element(*self.locator).text
        else:
            return (
                obj.driver.find_element(*self.locator)
                .get_attribute(self.name_attribite))


class _BaseButton():
    def __init__(self, locator: Locator):
        self.locator = locator

    def __set__(self, obj, value):
        button = obj.driver.find_element(*self.locator)
        button.click()


class LoginPage(_BasePage):
    field_login = _BaseElement(LoginPage_locators.LOGIN)
    field_password = _BaseElement(LoginPage_locators.PASSWORD)
    come_in_button = _BaseButton(LoginPage_locators.OK_BUTTON)

    def __init__(self, driver, login: str, password: str):
        super().__init__(driver)
        self.login = login
        self.password = password

    def handle(self, request: list[TaskType]):
        self.field_login = self.login
        self.field_password = self.password
        self.come_in_button = click()
        return super().handle(request)


class BackofficePage(_BasePage):
    inventory = _BaseElement(BackofficePage_locators.INVENTORY_LINK)
    paid_inventory = _BaseElement(BackofficePage_locators.PAID_INVENTORY_LINK)
    orders_maid = _BaseElement(BackofficePage_locators.ORDERS_MADE_LINK)

    order_link = _BaseButton(BackofficePage_locators.ORDER_LINK)

    def get_table_from_page(self) -> BackofficeData:
        return BackofficeData(
            Decimal(self.inventory if self.inventory else 0),
            Decimal(self.paid_inventory if self.paid_inventory else 0),
            Decimal(self.orders_maid if self.orders_maid else 0)
            )

    def handle(self, request: list[TaskType]):

        if TaskType.GET_SUMMARY_INFORMATION in request:
            self.result_all_page.back_ofice_data = self.get_table_from_page()

        self.order_link = click()
        return super().handle(request)


class WarehouseSelectionPage(_BasePage):
    next_button = _BaseButton(WarehouseSelectionPage_locators.NEXT__BUTTON)

    def handle(self, request: list[TaskType]):
        self.next_button = click()
        return super().handle(request)


class NewOrderPage(_BasePage):
    other_block = _BaseElement(NewOrderPage_locators.OTHER_LINK)

    def get_table_from_page(self, categories: Products_category) -> Table:

        # ожидание прогрузки всего списка
        _ = self.other_block

        table = []
        for cat in categories:
            elem_cat = self.driver.find_element(*NewOrderPage_locators.category_link(cat))
            elem_cat.click()

            # нажимаем кнопку Показать еще ... столько раз сколько появится
            have_error = click_all_next_button(self.driver, NewOrderPage_locators.SHOW_MORE_LINK)
            if have_error["have_error"]:
                print(f" ошибка в категории: {elem_cat.text}")
                print(have_error)
            # собираем в один список все строчки
            table.extend(
                get_table_data(
                    self.driver,
                    NewOrderPage_locators.GOODS_LINE,
                    cat,
                    True,
                    False
                    ))
        return table

    def handle(self, request: list[TaskType]):
        if TaskType.AVIABLE_POINT_PRODUCTS in request:
            self.result_all_page.aviable_point_products = (
                self.get_table_from_page(NewOrderPage_locators.POINT_CATEGORYS))

        elif TaskType.AVIABLE_COUPON_PRODUCTS in request:
            self.result_all_page.aviable_point_products = (
                self.get_table_from_page(NewOrderPage_locators.COUPON_CATEGORYS))

        elif TaskType.AVIABLE_LEFTOVERS_PRODUCTS in request:
            self.result_all_page.aviable_point_products = (
                self.get_table_from_page(NewOrderPage_locators.LEFTOVER_CATEGORYS))

        return super().handle(request)
