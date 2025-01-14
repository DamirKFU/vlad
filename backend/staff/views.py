import json

import django.db.transaction
import rest_framework.generics
import rest_framework.permissions
import rest_framework.status
import rest_framework.views

import catalog.models
import core.elasticsearch
import core.utils
import staff.documets
import staff.models
import staff.pagination
import staff.serializers
import staff.utils
import support.models
import support.serializers
import users.models


class StaffOrderListView(rest_framework.generics.ListAPIView):
    serializer_class = staff.serializers.StaffOrderSerializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    pagination_class = staff.pagination.OrderStaffPagination

    def get_queryset(self, status):
        return catalog.models.Order.objects.get_orders_for_staff(status=status)

    def get(self, request, *args, **kwargs):
        if not request.user.roles.exists() and not request.user.is_superuser:
            return core.utils.error_response(
                message="У вас нет доступа к этому разделу",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        status = self.request.query_params.get("status")
        if not status:
            return core.utils.error_response(
                message="Не указан статус заказов",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        allowed_statuses = staff.utils.get_allowed_statuses(request.user)
        if status not in allowed_statuses:
            return core.utils.error_response(
                fields={
                    "status": "У вас нет доступа к заказам с данным статусом",
                },
                message="Доступ запрещен",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        queryset = self.get_queryset(status)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated_response = self.get_paginated_response(serializer.data).data

        response_data = {
            **paginated_response,
            "allowed_statuses": allowed_statuses,
        }

        return core.utils.success_response(
            data=response_data,
            message="Заказы успешно получены",
        )


class StaffOrderDetailView(rest_framework.views.APIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def _get_serializer(self, order):
        if order.status == catalog.models.OrderStatus.IN_WORK:
            return staff.serializers.InWorkOrderSerializer(
                order, context={"request": self.request}
            )

        if order.status == catalog.models.OrderStatus.DRAFT:
            return staff.serializers.DraftOrderSerializer(
                order, context={"request": self.request}
            )

        if order.status == catalog.models.OrderStatus.IN_DELIVERY:
            return staff.serializers.InDeliveryOrderSerializer(
                order, context={"request": self.request}
            )

        if order.status == catalog.models.OrderStatus.PAID:
            return staff.serializers.PaidOrderSerializer(
                order, context={"request": self.request}
            )

        return staff.serializers.StaffOrderDetailSerializer(
            order, context={"request": self.request}
        )

    def get_object(self):
        order = catalog.models.Order.objects.get_order_status(
            order_id=self.kwargs["order_id"]
        )
        if not order:
            return None

        if order.status == catalog.models.OrderStatus.PAID:
            return catalog.models.Order.objects.get_paid_order_detail(
                order_id=self.kwargs["order_id"]
            )

        if order.status == catalog.models.OrderStatus.IN_WORK:
            return catalog.models.Order.objects.get_in_work_order_detail(
                order_id=self.kwargs["order_id"]
            )

        if order.status == catalog.models.OrderStatus.DRAFT:
            return catalog.models.Order.objects.get_draft_order_detail(
                order_id=self.kwargs["order_id"]
            )

        if order.status == catalog.models.OrderStatus.IN_DELIVERY:
            return catalog.models.Order.objects.get_in_delivery_order_detail(
                order_id=self.kwargs["order_id"]
            )

        if order.status == catalog.models.OrderStatus.DELIVERED:
            return catalog.models.Order.objects.get_delivered_order_detail(
                order_id=self.kwargs["order_id"]
            )

        return None

    def check_order_permissions(self, request, order):
        if not request.user.roles.exists() and not request.user.is_superuser:
            return False

        allowed_statuses = staff.utils.get_allowed_statuses(request.user)
        if order.status not in allowed_statuses:
            return False

        return True

    def get(self, request, order_id, *args, **kwargs):
        order = self.get_object()
        if not order:
            return core.utils.error_response(
                message="Заказ не найден",
                http_status=rest_framework.status.HTTP_404_NOT_FOUND,
            )

        if not self.check_order_permissions(request, order):
            return core.utils.error_response(
                message="У вас нет доступа к этому разделу",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        serializer = self._get_serializer(order)
        return core.utils.success_response(
            data=serializer.data,
            message="Заказ успешно получен",
        )

    @django.db.transaction.atomic
    def post(self, request, order_id, *args, **kwargs):
        order = self.get_object()
        if not order:
            return core.utils.error_response(
                message="Заказ не найден",
                http_status=rest_framework.status.HTTP_404_NOT_FOUND,
            )

        if not self.check_order_permissions(request, order):
            return core.utils.error_response(
                message="У вас нет доступа к этому разделу",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        handlers = {
            catalog.models.OrderStatus.DRAFT: self._handle_draft_forward,
            catalog.models.OrderStatus.IN_WORK: self._handle_in_work_forward,
            catalog.models.OrderStatus.PAID: self._handle_paid_forward,
            catalog.models.OrderStatus.IN_DELIVERY: (
                self._handle_in_delivery_forward
            ),
        }

        handler = handlers.get(order.status)
        if not handler:
            return core.utils.error_response(
                message="Недопустимый статус",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        return handler(order, request.data)

    @django.db.transaction.atomic
    def delete(self, request, order_id, *args, **kwargs):
        order = self.get_object()
        if not order:
            return core.utils.error_response(
                message="Заказ не найден",
                http_status=rest_framework.status.HTTP_404_NOT_FOUND,
            )

        if not self.check_order_permissions(request, order):
            return core.utils.error_response(
                message="У вас нет доступа к этому разделу",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        handlers = {
            catalog.models.OrderStatus.DRAFT: self._handle_draft_return,
            catalog.models.OrderStatus.IN_WORK: self._handle_in_work_return,
            catalog.models.OrderStatus.IN_DELIVERY: (
                self._handle_in_delivery_return
            ),
        }

        handler = handlers.get(order.status)
        if not handler:
            return core.utils.error_response(
                message="Возврат невозможен",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        return handler(order, request.data)

    def _handle_draft_forward(self, order, data):
        serializer = staff.serializers.DraftForwardSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.forward(order, self.request.user)
        return self._get_success_response(order)

    def _handle_draft_return(self, order, data):
        serializer = staff.serializers.ReturnOrderSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.return_to_status(
            order, self.request.user, catalog.models.OrderStatus.IN_WORK
        )
        return self._get_success_response(order)

    def _handle_in_work_forward(self, order, data):
        serializer = staff.serializers.InWorkForwardSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.forward(order, self.request.user)
        return self._get_success_response(order)

    def _handle_in_work_return(self, order, data):
        serializer = staff.serializers.ReturnOrderSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.return_to_status(
            order, self.request.user, catalog.models.OrderStatus.PAID
        )
        return self._get_success_response(order)

    def _handle_paid_forward(self, order, data):
        json_data = data.get("items")
        if json_data is None:
            return core.utils.error_response(
                message="Не указаны элементы заказа",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        items_data = json.loads(json_data)

        embroidery_files = {}
        try:
            for key, value in self.request.FILES.items():
                if key.startswith("embroidery_"):
                    index = int(key.split("_")[1])
                    embroidery_files[index] = value
        except IndexError:
            return core.utils.error_response(
                fields={
                    "items": {
                        "embroidery": "файл должен имет"
                        "формат filename_{index}"
                    }
                },
                message="неправильные имена файлов",
            )

        for item in items_data:
            if item["id"] in embroidery_files:
                item["embroidery"] = embroidery_files[index]

        data = {"items": items_data}
        serializer = staff.serializers.PaidForwardSerializer(
            data=data, context={"order": order}
        )

        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.forward(order, self.request.user)
        return self._get_success_response(order)

    def _handle_in_delivery_forward(self, order, data):
        serializer = staff.serializers.InDeliveryForwardSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.forward(order, self.request.user)
        return self._get_success_response(order)

    def _handle_in_delivery_return(self, order, data):
        serializer = staff.serializers.ReturnOrderSerializer(data=data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.return_to_status(
            order, self.request.user, catalog.models.OrderStatus.DRAFT
        )
        return self._get_success_response(order)

    def _get_success_response(self, order):
        return core.utils.success_response(
            data=order.status,
            message="Статус заказа успешно обновлен",
        )


class OrderLogListView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    pagination_class = staff.pagination.OrderStaffPagination

    def get(self, request, order_id, *args, **kwargs):
        if not (
            request.user.is_superuser
            or request.user.roles.filter(
                role=users.models.Role.MODERATOR
            ).exists()
        ):
            return core.utils.error_response(
                message="У вас нет доступа к этому разделу",
                http_status=rest_framework.status.HTTP_403_FORBIDDEN,
            )

        page = request.query_params.get("page", 1)
        if not page.isdigit():
            return core.utils.error_response(
                message="Некорректная страница",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        page = int(page)
        page_size = self.pagination_class.page_size
        response = staff.documets.OrderLogDocument.search_by_order_id(
            order_id, page_size, page
        )
        total = response.hits.total.value
        logs = [
            {
                "username": hit.username,
                "from_status": hit.from_status,
                "to_status": hit.to_status,
                "error_comment": hit.error_comment,
                "created_at": hit.created_at,
            }
            for hit in response
        ]
        total_pages = (total + page_size - 1) // page_size

        data = {
            "count": total,
            "total_pages": total_pages,
            "next": page < total_pages,
            "previous": page > 1,
            "results": logs,
        }

        return core.utils.success_response(
            data=data,
            message="История изменений успешно получена",
        )


class StaffChatListView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_class = support.serializers.ChatSerializer

    def get_queryset(self):
        return support.models.Chat.objects.get_chats_for_staff(
            self.request.user, self.kwargs.get("chat_type")
        )

    def get(self, request, *args, **kwargs):
        chat_type = self.kwargs.get("chat_type")

        if chat_type not in ["my", "unassigned", "assigned"]:
            return core.utils.error_response(message="Неверный тип чатов")

        if chat_type == "assigned" and not request.user.is_superuser:
            return core.utils.error_response(message="Недостаточно прав")

        try:
            data = super().get(request, *args, **kwargs).data
        except Exception:
            return core.utils.error_response(message="Ошибка получения чатов")

        return core.utils.success_response(
            message="Чаты получены",
            data=data,
        )

    @django.db.transaction.atomic
    def post(self, request, *args, **kwargs):
        chat_type = self.kwargs.get("chat_type")

        if chat_type != "unassigned":
            return core.utils.error_response(
                message="Действие доступно только для чатов без ответственных"
            )

        serializer = staff.serializers.StaffChatResponsibleUserSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                message="Ошибка валидации",
                serializer_errors=serializer.errors,
            )

        serializer.save()

        return core.utils.success_response(
            message="Вы успешно присоединились к чату"
        )
