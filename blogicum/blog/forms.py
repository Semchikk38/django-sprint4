from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment, Category

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Текст комментария'}
            ),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        self.fields['category'].required = False
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class BlogUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
