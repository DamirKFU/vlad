from pathlib import Path
import uuid

import django.core.validators
import django.db.models
import django.utils.safestring
import sorl.thumbnail

import catalog.validators
import users.models


def get_path_image(instance, filename):
    ext = Path(filename).suffix
    return f"catalog/{uuid.uuid4()}{ext}"


class Size(django.db.models.TextChoices):
    XS = "XS", "XS"
    S = "S", "S"
    M = "M", "M"
    L = "L", "L"
    XL = "XL", "XL"
    XXL = "XXL", "XXL"


class ConstructorProductStatus(django.db.models.TextChoices):
    IN_MODERATION = "IM", "На модерации"
    ACCEPTED = "AC", "Принято"
    REJECTED = "RJ", "Отказано"


class BaseImage(django.db.models.Model):
    image = sorl.thumbnail.ImageField(
        "изображение",
        upload_to=get_path_image,
        help_text="загрузите изображение",
    )

    def get_image_300x300(self):
        return sorl.thumbnail.get_thumbnail(
            self.image,
            "300x300",
            crop="center",
            quality=100,
        )

    def image_tmb(self):
        if self.image:
            tag = f'<img src="{self.get_image_300x300().url}">'
            return django.utils.safestring.mark_safe(tag)

        return "изображение отсутствует"

    image_tmb.short_description = "превью"
    image_tmb.allow_tags = True
    image_tmb.field_name = "image_tmb"

    class Meta:
        verbose_name = "абстрактная модель изображения"
        verbose_name_plural = "абстрактные модели изображений"
        abstract = True

    def __str__(self):
        return Path(self.image.path).stem


class AbstractModel(django.db.models.Model):
    name = django.db.models.CharField(
        "название",
        max_length=150,
        unique=True,
        help_text="напишите название",
    )

    class Meta:
        verbose_name = "абстрактная модель"
        verbose_name_plural = "абстрактные модели"
        abstract = True

    def __str__(self) -> str:
        return self.name


class Category(AbstractModel):
    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Color(AbstractModel):
    color = django.db.models.CharField(
        "hex цвета",
        max_length=7,
        validators=[
            catalog.validators.HexColorValidator(),
        ],
        help_text="напишите hex цвета иммет формат #008000",
    )

    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "цвета"


class GarmentManager(django.db.models.Manager):
    def all_items(self):
        queryset = (
            super()
            .get_queryset()
            .filter(count__gt=0)
            .select_related(
                Garment.category.field.name,
                Garment.color.field.name,
            )
        )
        return queryset.values(
            Garment.id.field.name,
            Garment.size.field.name,
            Garment.count.field.name,
            f"{Garment.category.field.name}__{Category.name.field.name}",
            f"{Garment.color.field.name}__{Color.name.field.name}",
            f"{Garment.color.field.name}__{Color.color.field.name}",
        )

    def items_by_category(self, category):
        return self.all_items().filter(category=category)

    def items_by_product_detail(self, product):
        return self.all_items().filter(products=product)


class Garment(django.db.models.Model):
    objects = GarmentManager()

    category = django.db.models.ForeignKey(
        Category,
        on_delete=django.db.models.CASCADE,
        verbose_name="категория",
        related_name="tshirts",
        related_query_name="tshirts",
        help_text="выберите категорию",
    )
    color = django.db.models.ForeignKey(
        Color,
        on_delete=django.db.models.CASCADE,
        verbose_name="цвет",
        related_name="tshirts",
        related_query_name="tshirts",
        help_text="выберите цвет",
    )
    size = django.db.models.CharField(
        "размер",
        choices=Size.choices,
        help_text="выберите размер",
        max_length=3,
    )

    count = django.db.models.PositiveIntegerField(
        "количество",
        help_text="укажите количество",
        default=0,
        validators=[
            django.core.validators.MinValueValidator(0),
        ],
    )
    price = django.db.models.PositiveIntegerField(
        "цена",
        help_text="цена одежды",
        default=0,
    )

    class Meta:
        verbose_name = "одежда"
        verbose_name_plural = "одежды"

        unique_together = (
            "category",
            "color",
            "size",
        )

    def __str__(self) -> str:
        return f"Одежда({self.category}, {self.color}, {self.size})"


class ConstructorProduct(django.db.models.Model):
    garment = django.db.models.ForeignKey(
        Garment,
        on_delete=django.db.models.CASCADE,
        verbose_name="одежда",
        help_text="одежда товара",
        related_name="construct_products",
        related_query_name="construct_products",
    )
    status = django.db.models.CharField(
        "статус модерации",
        choices=ConstructorProductStatus.choices,
        default=ConstructorProductStatus.IN_MODERATION,
        help_text="выберите статус",
        max_length=2,
    )
    user = django.db.models.ForeignKey(
        users.models.User,
        on_delete=django.db.models.CASCADE,
        verbose_name="пользователь",
        help_text="пользователь, отправивший запрос",
        related_name="construct_products",
        related_query_name="construct_products",
    )

    class Meta:
        verbose_name = "товар конструктора"
        verbose_name_plural = "товары конструктора"

    def __str__(self):
        return "Товар Конструктора"


class ConstructorProductImage(BaseImage):
    product = django.db.models.OneToOneField(
        ConstructorProduct,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="image",
        related_query_name="image",
    )

    class Meta:
        verbose_name = "изображение товара конструктора"
        verbose_name_plural = "изображения товаров конструктора"


class ConstructorEmbroideryImage(BaseImage):
    product = django.db.models.OneToOneField(
        ConstructorProduct,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="embroidery_image",
        related_query_name="embroidery_image",
    )

    class Meta:
        verbose_name = "изображение вышивки"
        verbose_name_plural = "изображения вышивки"


class Product(AbstractModel):

    price = django.db.models.PositiveIntegerField(
        "цена",
        help_text="цена товара",
        default=0,
    )
    garments = django.db.models.ManyToManyField(
        Garment,
        verbose_name="одежды",
        help_text="одежда товара",
        related_name="products",
        related_query_name="products",
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return f"Товар({self.name})"


class ProductImage(BaseImage):
    product = django.db.models.OneToOneField(
        Product,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="image",
        related_query_name="image",
    )

    def image_tmb(self):
        if self.image:
            tag = f'<img src="{self.get_image_660x880().url}">'
            return django.utils.safestring.mark_safe(tag)

        return "изображение отсутствует"

    def get_image_660x880(self):
        return sorl.thumbnail.get_thumbnail(
            self.image,
            "660x880",
            upscale=False,
            crop=False,
            quality=100,
        )

    class Meta:
        verbose_name = "изображение товара"
        verbose_name_plural = "изображения товаров"


class ProductAdditionalImageManager(django.db.models.Manager):
    def get_images_for_garments(self, product, garments_data):
        return (
            self.get_queryset()
            .select_related("category", "color")
            .filter(
                product=product,
                category__in=garments_data.values("category"),
                color__in=garments_data.values("color"),
            )
        )


class ProductAdditionalImage(BaseImage):
    objects = ProductAdditionalImageManager()

    product = django.db.models.ForeignKey(
        Product,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар дополнительного изображения",
        related_name="additional_images",
        related_query_name="additional_images",
    )
    category = django.db.models.ForeignKey(
        Category,
        on_delete=django.db.models.CASCADE,
        verbose_name="категория",
        help_text="категория дополнительного изображения",
        related_name="additional_images",
        related_query_name="additional_images",
    )
    color = django.db.models.ForeignKey(
        Color,
        on_delete=django.db.models.CASCADE,
        verbose_name="цвет",
        help_text="цвет дополнительного изображения",
        related_name="additional_images",
        related_query_name="additional_images",
    )

    def image_tmb(self):
        if self.image:
            tag = f'<img src="{self.get_image_330x440().url}">'
            return django.utils.safestring.mark_safe(tag)

        return "изображение отсутствует"

    def get_image_330x440(self):
        return sorl.thumbnail.get_thumbnail(
            self.image,
            "330x440",
            upscale=False,
            crop=False,
            quality=100,
        )

    class Meta:
        verbose_name = "дополнительное изображение товара"
        verbose_name_plural = "дополнительные изображения товаров"


class CartManager(django.db.models.Manager):
    def get_cart_with_items(self):
        image_subquery = (
            ProductAdditionalImage.objects.filter(
                product_id=django.db.models.OuterRef("product_id"),
                category_id=django.db.models.OuterRef("garment__category_id"),
                color_id=django.db.models.OuterRef("garment__color_id"),
            )
            .order_by("id")
            .values("image")[:1]
        )
        return (
            super()
            .get_queryset()
            .prefetch_related(
                django.db.models.Prefetch(
                    Cart.items.field.related_query_name(),
                    queryset=(
                        CartItem.objects.select_related(
                            CartItem.cart.field.name,
                            CartItem.product.field.name,
                            (
                                f"{CartItem.product.field.name}"
                                f"__{Product.image.related.name}"
                            ),
                            CartItem.garment.field.name,
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.color.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.category.field.name}"
                            ),
                        )
                        .annotate(
                            matching_image=django.db.models.Subquery(
                                image_subquery
                            )
                        )
                        .only(
                            (
                                f"{CartItem.cart.field.name}"
                                f"__{Cart.id.field.name}"
                            ),
                            CartItem.quantity.field.name,
                            (
                                f"{CartItem.product.field.name}"
                                f"__{Product.name.field.name}"
                            ),
                            (
                                f"{CartItem.product.field.name}"
                                f"__{Product.price.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.size.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.count.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.price.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.color.field.name}"
                                f"__{Color.color.field.name}"
                            ),
                            (
                                f"{CartItem.garment.field.name}"
                                f"__{Garment.category.field.name}"
                                f"__{Category.name.field.name}"
                            ),
                        )
                    ),
                )
            )
        )

    def get_cart_for_order(self, user):
        return (
            self.filter(user=user)
            .select_related("user")
            .prefetch_related(
                django.db.models.Prefetch(
                    "items",
                    queryset=CartItem.objects.select_related(
                        "product",
                        "garment",
                    ),
                ),
            )
            .first()
        )


class Cart(django.db.models.Model):
    objects = CartManager()
    user = django.db.models.OneToOneField(
        users.models.User,
        verbose_name="пользователь",
        help_text="пользователь корзины",
        on_delete=django.db.models.CASCADE,
        related_name="cart",
        related_query_name="cart",
    )

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"


class CartItem(django.db.models.Model):
    cart = django.db.models.ForeignKey(
        Cart,
        verbose_name="корзина",
        help_text="корзина",
        on_delete=django.db.models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    product = django.db.models.ForeignKey(
        Product,
        verbose_name="товар",
        help_text="товар предмета корзины",
        on_delete=django.db.models.CASCADE,
    )
    garment = django.db.models.ForeignKey(
        Garment,
        verbose_name="одежда",
        help_text="одежда предмета корзины",
        on_delete=django.db.models.CASCADE,
    )
    quantity = django.db.models.PositiveIntegerField(
        "количество",
        help_text="количество предмета в корзине",
        default=1,
        validators=[
            django.core.validators.MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = "предмет корзины"
        verbose_name_plural = "предметы корзины"

    @property
    def total_price(self):
        return (self.product.price + self.garment.price) * self.quantity


class OrderStatus(django.db.models.TextChoices):
    WAITING_PAYMENT = "WP", "Ожидает оплаты"
    PAID = "PD", "В разработке"
    IN_WORK = "IW", "На шитье"
    IN_DELIVERY = "ID", "В доставке"
    DELIVERED = "DV", "Доставлен"
    CANCELED = "CN", "Отменён"


class PaymentStatus(django.db.models.TextChoices):
    PENDING = "pending", "В ожидании"
    SUCCEEDED = "succeeded", "Успешно"
    CANCELED = "canceled", "Отменён"


class OrderManager(django.db.models.Manager):
    def delete(self, *args, **kwargs):
        raise Exception("Orders cannot be deleted, use cancel_order() instead")

    def bulk_delete(self, *args, **kwargs):
        raise Exception("Orders cannot be deleted, use cancel_order() instead")

    def get_orders_with_items(self, user):
        image_subquery = (
            ProductAdditionalImage.objects.filter(
                product_id=django.db.models.OuterRef("product_id"),
                category_id=django.db.models.OuterRef("garment__category_id"),
                color_id=django.db.models.OuterRef("garment__color_id"),
            )
            .order_by("id")
            .values("image")[:1]
        )

        return (
            self.filter(user=user)
            .select_related("user")
            .prefetch_related(
                django.db.models.Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related(
                        "product",
                        "garment__category",
                        "garment__color",
                    )
                    .annotate(
                        matching_image=django.db.models.Subquery(
                            image_subquery
                        )
                    )
                    .only(
                        "order__id",
                        "garment__category__name",
                        "garment__color__color",
                        "garment__size",
                        "product__name",
                        "quantity",
                        "price",
                    ),
                ),
            )
            .only(
                "id",
                "status",
                "items",
                "address",
                "total_sum",
                "user__id",
                "created_at",
            )
        )

    def get_orders_for_detail(self, user):
        return self.get_orders_with_items(user).only(
            "id",
            "status",
            "items",
            "address",
            "phone",
            "total_sum",
            "user__id",
            "user__email",
            "payment_status",
            "confirmation_url",
            "payment_id",
            "created_at",
        )


class Order(django.db.models.Model):
    objects = OrderManager()

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name="пользователь",
        on_delete=django.db.models.CASCADE,
        related_name="orders",
    )
    address = django.db.models.CharField(
        "адрес доставки",
        max_length=255,
        help_text="адрес доставки заказа",
    )
    status = django.db.models.CharField(
        "статус заказа",
        max_length=2,
        choices=OrderStatus.choices,
        default=OrderStatus.WAITING_PAYMENT,
        help_text="статус заказа",
    )
    created_at = django.db.models.DateTimeField(
        "дата создания",
        auto_now_add=True,
        help_text="дата создания заказа",
    )
    updated_at = django.db.models.DateTimeField(
        "дата обновления",
        auto_now=True,
        help_text="дата обновления заказа",
    )
    phone = django.db.models.CharField(
        "номер телефона",
        max_length=15,
        help_text="номер телефона пользователя",
        validators=[
            catalog.validators.validate_russian_phone,
        ],
    )
    total_sum = django.db.models.PositiveIntegerField(
        "сумма заказа",
        help_text="сумма заказа",
        validators=[
            django.core.validators.MinValueValidator(0),
        ],
        default=0,
    )
    payment_id = django.db.models.CharField(
        "идентификатор платежа",
        help_text="идентификатор платежа в платежной системе",
        max_length=255,
        blank=True,
        null=True,
    )
    payment_status = django.db.models.CharField(
        "статус платежа",
        help_text="статус платежа в платежной системе",
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    confirmation_url = django.db.models.URLField(
        "url для подтверждения платежа",
        help_text="url для подтверждения платежа",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        ordering = ["-created_at"]
        constraints = [
            django.db.models.UniqueConstraint(
                fields=["user", "status"],
                name="unique_user_waiting_payment",
                condition=django.db.models.Q(
                    status=OrderStatus.WAITING_PAYMENT
                ),
            )
        ]

    def cancel_order(self):
        if self.status == OrderStatus.WAITING_PAYMENT:
            for order_item in self.items.select_related("garment").all():
                order_item.garment.count += order_item.quantity
                order_item.garment.save()

            self.status = OrderStatus.CANCELED
            self.payment_status = PaymentStatus.CANCELED
            self.save()

    def delete(self, *args, **kwargs):
        raise Exception("Orders cannot be deleted, use cancel_order() instead")

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderItem(django.db.models.Model):
    order = django.db.models.ForeignKey(
        Order,
        verbose_name="заказ",
        help_text="заказ предмета",
        on_delete=django.db.models.CASCADE,
        related_name="items",
        related_query_name="items",
    )
    product = django.db.models.ForeignKey(
        Product,
        verbose_name="товар",
        help_text="товар предмета заказа",
        on_delete=django.db.models.PROTECT,
    )
    garment = django.db.models.ForeignKey(
        Garment,
        verbose_name="одежда",
        help_text="одежда предмета заказа",
        on_delete=django.db.models.PROTECT,
    )
    quantity = django.db.models.PositiveIntegerField(
        "количество",
        help_text="количество предмета в заказе",
        validators=[
            django.core.validators.MinValueValidator(1),
        ],
    )
    price = django.db.models.PositiveIntegerField(
        "цена",
        help_text="цена на момент заказа",
    )

    class Meta:
        verbose_name = "предмет заказа"
        verbose_name_plural = "предметы заказа"

    def __str__(self):
        return f"Предмет заказа №{self.order.id}"

    @property
    def total_price(self):
        return self.price * self.quantity
