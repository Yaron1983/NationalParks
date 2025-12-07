from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.views.generic import TemplateView
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = ChatRoom.objects.all()
        if self.request.user.is_authenticated:
            # Show public rooms and rooms user is a participant in
            queryset = queryset.filter(
                Q(is_public=True) | Q(participants=self.request.user)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        room = self.get_object()
        room.participants.add(request.user)
        return Response({'status': 'joined room'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        room = self.get_object()
        room.participants.remove(request.user)
        return Response({'status': 'left room'})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.request.query_params.get('room', None)
        queryset = Message.objects.all()
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        return queryset.order_by('timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatView(TemplateView):
    """View for displaying the chat interface"""
    template_name = 'chat/chat.html'

