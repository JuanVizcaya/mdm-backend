from rest_framework import serializers
from django.forms.fields import FileField
from .models import UploadFiles, UploadFilesTrack, FileMovements, VersionesLocalidades
from usuarios.serializers import VerUsuarioSerializer
from catalogos.models import Tmp_Cat_Entidades

class UploadFilesSerializer(serializers.ModelSerializer):
    catLoad = serializers.FileField()
    eqvLoad = serializers.FileField()
    actLoad = serializers.FileField()
    author = VerUsuarioSerializer(read_only=True)
    class Meta:
        model = UploadFiles
        fields = ['filesId','filesType','filesVersion','uploadedDate','author','status','statusDesc','processStep','buttons','nextStep','catLoad','eqvLoad','actLoad','catTable','eqvTable','actTable']

    def save(self, author):
        files = UploadFiles(
            filesType = self.validated_data['filesType'],
            filesVersion = self.validated_data['filesVersion'],
            author = author,
            catLoad = self.validated_data['catLoad'],
            eqvLoad = self.validated_data['eqvLoad'],
            actLoad = self.validated_data['actLoad']
            )
        files.save()
        return files
    
class UploadFilesListSerializer(serializers.ModelSerializer):
    author = VerUsuarioSerializer(read_only=True)
    class Meta:
        model = UploadFiles
        fields = ['filesId','filesType','filesVersion','uploadedDate','author','status','statusDesc','processStep','buttons','nextStep']
        
class FileMovementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileMovements
        fields = ['UploadFiles', 'cgo_act', 'descgo_act', 'mov_cant', 'move_type']

class TmpEntidadesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tmp_Cat_Entidades
        fields = (
            'id',
            'snap_id',
            'ent',
            'cve_ent',
            'nom_ent',
            'abr_ent',
            'p_total',
            'v_total',
            'p_mas',
            'p_fem',
            'cgo_act',
            'descgo_act',
            'mov_inegi'
        )

class VersionesLocalidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionesLocalidades
        fields = ['tipo', 'version', 'fecha_carga', 'num_regs', 'vigente']
        