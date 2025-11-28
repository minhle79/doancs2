from django import forms
from django.contrib.auth.models import User
from .models import Order


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Xác nhận mật khẩu")

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Mật khẩu xác nhận không khớp")
        return cleaned


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "address", "note"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Nhập họ"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Nhập tên"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
        }


