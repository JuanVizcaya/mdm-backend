from rest_framework import serializers
from .models import Usuario

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = Usuario
        fields = ['email','first_name','last_name','password','password2']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        usuario = Usuario(
            email = self.validated_data['email'],
            first_name = self.validated_data['first_name'],
            last_name = self.validated_data['last_name']
            )
        password1 = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password1 != password2:
            raise serializers.ValidationError({'error': 'las contraseñas no coinciden'})
        
        usuario.set_password(password1)
        usuario.save()
        return usuario
    
class VerUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email','first_name','last_name']