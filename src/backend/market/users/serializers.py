from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from users.models import UserProfile, Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer контактов пользователя.
    """
    class Meta:
        model = Contact
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer
    """
    class Meta:
        model = UserProfile
        fields = ('middle_name',)


class UserSerializer(UserDetailsSerializer):
    """
    Update user profile and contacts.
    """
    contacts = ContactSerializer()
    profile = UserProfileSerializer()

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('id', 'contacts', 'profile')

    def update(self, instance, validated_data):
        user_contacts_serializer = self.fields['contacts']
        user_contacts_instance = instance.contacts
        user_contacts_data = validated_data.pop('contacts', {})
        user_contacts_serializer.update(user_contacts_instance, user_contacts_data)

        user_profile_serializer = self.fields['profile']
        user_profile_instance = instance.profile
        user_profile_data = validated_data.pop('profile', {})
        user_profile_serializer.update(user_profile_instance, user_profile_data)

        instance = super().update(instance, validated_data)
        return instance
