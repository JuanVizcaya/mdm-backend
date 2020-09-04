from ..models import UploadFilesTrack
from django.utils import timezone

class Tracking(object):
    def __init__(self, filesLoad, steps, startStep):
        self.filesLoad = filesLoad
        self.steps = steps
        self.save_step(startStep, firstTrack=True)
    
    def save_step(self, stepNumber='0', firstTrack=False, lastTrack=False, error=False, errorData={'status': 'error', 'statusDesc': 'Default error'}):
        startTime = timezone.now()
        if not firstTrack:
            self.lastTrack.endTime = timezone.now()
            self.lastTrack.save()
            startTime = self.lastTrack.endTime            

        data = self.steps[stepNumber]
        if error:
            lastTrack = True
            data['status'] = errorData['status']
            data['statusDesc'] = errorData['statusDesc']
        self.lastTrack = UploadFilesTrack.objects.create(
            UploadFiles = self.filesLoad,
            stepNumber = (stepNumber, -3)[error],
            startTime = startTime,
            endTime = (None, timezone.now())[lastTrack],
            status = data['status'],
            statusDesc = data['statusDesc'],
            processStep = (data['processStep'],'error')[error],
            activo = (data['activo'], 0)[error],
            buttons = (data['buttons'], '0-0-0-0-1')[error],
            nextStep = (data['nextStep'], '-')[error]
        )
        return self.lastTrack
