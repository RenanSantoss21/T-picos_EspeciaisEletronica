import os
import sys
import django

sys.path.append(r'c:\Users\willi\OneDrive\Documentos\Documentos\RENAN_DOCS\2026.1\TópicosEspeciaisEletronica\ControleEstProcessos')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cartaControle.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user, created = User.objects.get_or_create(username='willi', email='willi@example.com')
user.set_password('RenanSantos21')
user.is_superuser = True
user.is_staff = True
user.save()

Token.objects.filter(user=user).delete()
Token.objects.create(user=user, key='2c9e16fd4425e31be2d9bb6678e333bee6ea7bf7')

print("Usuário e token configurados com sucesso.")
