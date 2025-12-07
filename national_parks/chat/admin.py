from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'content', 'timestamp', 'edited']
    list_filter = ['room', 'timestamp', 'edited']
    search_fields = ['content', 'user__username']
    readonly_fields = ['timestamp', 'edited_at']

