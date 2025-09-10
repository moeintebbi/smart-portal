from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User , Course , Comment , Lesson
from django_summernote.widgets import SummernoteWidget

class Registerform(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

def save(self, commit=True):
    user = super().save(commit=False)
    user.role = 'student'
    if commit:
        user.save()  
    return user


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'image', 'descriptions', 'capacity', 'days', 'start_time', 'end_time', 'prerequisites']
        widgets = {
            'prerequisites': forms.CheckboxSelectMultiple(),
        }

class StudentInfoForm(forms.Form):
    full_name = forms.CharField(label= 'نام و نام خانوادگی خود را وارد کنید' , max_length=100)
    email = forms.EmailField(label='ایمیل خود را وارد کنید')
    education_level = forms.CharField(label='مقطع تحصیلی خود را وارد کنید' , max_length=100)
    


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'متن نظر',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'نظر خود را وارد کنید...'
            }),
            }
        
class PasswordRestRequestForm(forms.Form):
    email = forms.EmailField(label='ایمیل خود را وارد کنید')

class CodeVerficationForm(forms.Form):
    code = forms.CharField(label='کد تأیید', max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control text-center',
        'placeholder': 'مثال: 924157',
        'id': 'code'
    }))
    new_password = forms.CharField(label='رمز عبور جدید', widget=forms.PasswordInput(attrs={
        'class': 'form-control text-center',
        'placeholder': 'رمز عبور جدید',
        'id': 'new_password'
    }))


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'content':SummernoteWidget()
            }