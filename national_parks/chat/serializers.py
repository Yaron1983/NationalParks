from rest_framework import serializers
from .models import ChatRoom, Message
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = ['id', 'room', 'user', 'user_id', 'content', 'timestamp', 'edited', 'edited_at']
        read_only_fields = ['timestamp', 'edited', 'edited_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        write_only=True,
        required=False
    )
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'created_at', 'created_by',
            'participants', 'participant_ids', 'is_public',
            'message_count', 'last_message'
        ]
        read_only_fields = ['created_at', 'created_by']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': last_msg.id,
                'content': last_msg.content,
                'user': last_msg.user.username,
                'timestamp': last_msg.timestamp
            }
        return None

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        room = ChatRoom.objects.create(**validated_data)
        if participant_ids:
            room.participants.set(participant_ids)
        return room

