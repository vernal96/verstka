from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import (
    Profile,
    Photo,
    Student,
    Teacher,
    EducationalManager,
    Group,
    Dialog,
    DialogAttachment,
    Message,
    Category,
    Course,
    Lesson,
    Timetable,
    Certificate,
    AcademicPerformance,
)


class UserSerializer(serializers.ModelSerializer):
    """ Серилиазация базовой модели User
        Для отображения заявок в друзья и подписчиков
    """
    profile_id = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    date_of_birthday = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'profile_id', 'username', 'first_name', 'last_name', 'email', 'gender', 'date_of_birthday', 'avatar'
        ]

    @staticmethod
    def get_profile_id(obj):
        return obj.profile.id

    @staticmethod
    def get_gender(obj):
        return obj.profile.gender

    @staticmethod
    def get_date_of_birthday(obj):
        return obj.profile.date_of_birthday

    @staticmethod
    def get_avatar(obj):
        if obj.profile.avatar:
            return obj.profile.avatar.image.url
        else:
            return None


class ProfileSerializerBase(serializers.ModelSerializer):
    """ Базовый класс сериализации модели пользователей
        Родительский класс сериализации
    """
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'

    @staticmethod
    def get_username(obj):
        return obj.user.username

    @staticmethod
    def get_first_name(obj):
        return obj.user.first_name

    @staticmethod
    def get_last_name(obj):
        return obj.user.last_name

    @staticmethod
    def get_email(obj):
        return obj.user.email


class AvatarSerializer(serializers.ModelSerializer):
    """ Серилизация аватарки
    """
    class Meta:
        model = Photo
        fields = ['image']


class ProfileSerializer(ProfileSerializerBase):
    """ Сериализация модели профиля
        Для отображения пользователя в общем списке (не друзей)
    """
    avatar = AvatarSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'first_name', 'last_name', 'gender', 'avatar', 'user_group']


class ProfileCreateSerializer(serializers.ModelSerializer):
    """ Серилизатор полей модели профиля необходимых для регистрации пользователя
    """
    class Meta:
        model = Profile
        fields = ['middle_name', 'gender', 'phone', 'date_of_birthday']


class PhotoSerializer(serializers.ModelSerializer):
    """ Серилизация модели галереи
    """
    likes = ProfileSerializer(read_only=False, many=True)

    class Meta:
        model = Photo
        fields = ['id', 'image', 'date', 'likes']


class UploadPhotoSerializer(serializers.Serializer):
    """ Серилизация загрузки фото в галерею
    """
    image = serializers.ImageField()


class CreateProfileSerializer(serializers.Serializer):
    """ Серилизатор регистрации пользователя
    """
    username = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    profile = ProfileCreateSerializer()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        new_user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        new_user.set_password(validated_data['password'])
        new_user.save()

        profile_data = validated_data.pop('profile')
        Student.objects.create(
            user=new_user,
            middle_name=profile_data['middle_name'],
            phone=profile_data['phone'],
            gender=profile_data['gender'],
            date_of_birthday=profile_data['date_of_birthday']
        )

        return new_user


class EducationalManagerSerializer(ProfileSerializerBase):
    """ Сериализация модели менеджера учебного процесса
        Для отображения менеджера группы
    """
    class Meta:
        model = EducationalManager
        fields = [
            'id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'gender', 'phone', 'user_group'
        ]


class EducationalManagerDetailSerializer(ProfileSerializerBase):
    """ Сериализация детальной модели менеджера учебного процесса
        Для отображения в друзьях
    """
    photos = PhotoSerializer(read_only=False, many=True)
    friends = UserSerializer(read_only=True, many=True)
    friend_request_in = UserSerializer(read_only=True, many=True)
    friend_request_out = UserSerializer(read_only=True, many=True)

    class Meta:
        model = EducationalManager
        fields = [
            'id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'gender', 'phone',
            'date_of_birthday', 'photos', 'avatar', 'friends', 'friend_request_in', 'friend_request_out',
            'user_group'
        ]


class GroupSerializer(serializers.ModelSerializer):
    """ Сериализация модели групп
    """
    teacher = ProfileSerializer()
    manager = EducationalManagerSerializer()

    class Meta:
        model = Group
        fields = ['id', 'name', 'teacher', 'manager']


class TeacherDetailSerializer(ProfileSerializerBase):
    """ Сериализация модели преподавателей (видят друзья)
    """
    photos = PhotoSerializer(read_only=False, many=True)
    friends = UserSerializer(read_only=True, many=True)
    friend_request_in = UserSerializer(read_only=True, many=True)
    friend_request_out = UserSerializer(read_only=True, many=True)
    group_list = GroupSerializer(read_only=True, many=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'gender', 'phone',
            'date_of_birthday', 'education', 'professional_activity', 'group_list', 'photos', 'avatar', 'friends',
            'friend_request_in', 'friend_request_out', 'user_group'
        ]


class StudentDetailSerializer(ProfileSerializerBase):
    """ Сериализация детальной модели студентов (видят друзья)
    """
    group_list = GroupSerializer(read_only=True, many=True)
    photos = PhotoSerializer(read_only=False, many=True)
    friends = UserSerializer(read_only=True, many=True)
    friend_request_in = UserSerializer(read_only=True, many=True)
    friend_request_out = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Student
        fields = [
            'id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'gender', 'phone',
            'hobbies', 'dream', 'date_of_birthday', 'group_list', 'photos', 'avatar', 'friends', 'friend_request_in',
            'friend_request_out', 'user_group'
        ]


class CategorySerializer(serializers.ModelSerializer):
    """ Серилизация модели категирий курса
    """
    class Meta:
        model = Category
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """ Серилизация моделей курсов
    """
    category = CategorySerializer()
    teacher = ProfileSerializer()

    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    """ Серилизация модели всех уроков (только список без подробностей, видео и тд)
    """
    course = CourseSerializer()

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'theme', 'lesson_number']


class LessonRetrieveSerializer(LessonSerializer):
    """ Серилизация модели доступных уроков
    Для открытия конкретного урока доступного пользователю
    """
    class Meta:
        model = Lesson
        fields = '__all__'


class TimetableSerializer(serializers.ModelSerializer):
    """ Серилизация модели рассписания занятий
    """
    lesson = LessonSerializer()
    group = GroupSerializer()

    class Meta:
        model = Timetable
        fields = ['date', 'lesson', 'group', 'is_finished']


class TimetableCreateSerializer(serializers.ModelSerializer):
    """ Серилизация добавления урока рассписание занятий
    """
    class Meta:
        model = Timetable
        fields = ['date', 'lesson', 'group']

    def create(self, validated_data):
        return super().create(validated_data)


class CertificateSerializer(serializers.ModelSerializer):
    """ Серилизация модели сертификатов
    """
    profile = ProfileSerializerBase()
    course = CourseSerializer()

    class Meta:
        model = Certificate
        fields = ['profile', 'course', 'image', 'date']


class AcademicPerformanceSerializer(serializers.ModelSerializer):
    """ Серилизация модели успеваемости
    """
    class Meta:
        model = AcademicPerformance
        fields = [
            'student', 'lesson', 'teacher', 'date', 'homework_grade', 'classwork_grade', 'test_grade',
            'examination_grade', 'late', 'absent'
        ]

    def create(self, validated_data):
        return super().create(validated_data)


class DialogSerializer(serializers.ModelSerializer):
    """ Серилизация модели диалогов
    """
    participants = ProfileSerializer(read_only=False, many=True)

    class Meta:
        model = Dialog
        fields = '__all__'


class DialogAttachmentSerializer(serializers.ModelSerializer):
    """ Серилизация модели вложений к диалогу
    """
    dialog = DialogSerializer()

    class Meta:
        model = DialogAttachment
        fields = ['dialog', 'file']


class MessageSerializer(serializers.ModelSerializer):
    """ Серилизация отправки личных сообщений
    """
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)


class MessageViewSerializer(MessageSerializer):
    """ Серилизация чтения личных сообщений
    """
    from_user = ProfileSerializer()
    attachment = DialogAttachmentSerializer()

    class Meta:
        model = Message
        fields = ['id', 'from_user', 'attachment', 'text', 'date_and_time', 'is_read']
