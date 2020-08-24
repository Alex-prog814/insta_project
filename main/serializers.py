from rest_framework import serializers

from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S', read_only=True)

    class Meta:
        model = Post
        fields = ('text', 'image', 'created_at', 'id')

    def __get_image_url(self, instance):
        request = self.context.get('request')
        if instance.image:
            url = instance.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author_id'] = request.user.id
        post = Post.objects.create(**validated_data)
        return post

    def to_representation(self, instance):
        if 'comments' not in self.fields:
            self.fields['comments'] = CommentSerializer(instance, many=True)
        representation = super().to_representation(instance)
        representation['text'] = instance.text
        representation['author'] = instance.author.email
        representation['image'] = self.__get_image_url(instance)
        return representation
