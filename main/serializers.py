from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Post, Comment, Tag, Follow, PostImage

from main import services as likes_services

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', )

    def create(self, validated_data):
        user_to_follow = validated_data.get('user') #на кого подписаться
        user_who_is_following = self.context['request'].user #подписчик

        if Follow.objects.filter(user=user_to_follow, follower=user_who_is_following).exists():
            msg = "This user is already followings"
            raise serializers.ValidationError(msg)
        elif user_who_is_following.id == user_to_follow.id:
            msg = "User cannot follow itself"
            raise serializers.ValidationError(msg)
        else:
            follow = Follow.objects.create(
                user=user_to_follow,
                follower=user_who_is_following
            )
            return follow


class FanSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'full_name',
        )

    def get_full_name(self, obj):
        return obj.get_full_name()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'post_id', 'created_at', 'id')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author_id'] = request.user.id
        comment = Comment.objects.create(**validated_data)
        return comment

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['text'] = instance.text
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'slug')


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('images', )

    def _get_image_url(self, obj):
        if obj.images:
            url = obj.images.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = self._get_image_url(instance)
        return representation


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S', read_only=True)
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(), many=True, slug_field='slug')
    is_fan = serializers.SerializerMethodField()
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Post
        fields = ('text', 'images', 'created_at', 'id', 'tags', 'is_fan',  'total_likes')

    def get_is_fan(self, obj) -> bool:
        """Проверяет, лайкнул ли `request.user` твит (`obj`).
        """
        user = self.context.get('request').user
        return likes_services.is_fan(obj, user)

    def create(self, validated_data):
        print(validated_data)
        request = self.context.get('request')
        validated_data['author_id'] = request.user.id
        tags = validated_data.pop('tags')
        images = validated_data.pop('images')
        post = Post.objects.create(**validated_data)
        for tag in tags:
            post.tags.add(tag)
        print(images)
        for image in images:
            PostImage.objects.create(post=post, images=image)
        return post

    def to_representation(self, instance):
        if 'comments' not in self.fields:
            self.fields['comments'] = CommentSerializer(instance, many=True)
        representation = super().to_representation(instance)
        representation['text'] = instance.text
        representation['author'] = instance.author.email
        representation['images'] = PostImageSerializer(instance.images.all(), many=True, context=self.context).data
        return representation



