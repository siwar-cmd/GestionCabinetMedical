
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirmé'
        CANCELLED = 'CANCELLED', 'Annulé'

    doctor = models.ForeignKey(
        'AccountApp.Doctor',
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    patient = models.ForeignKey(
        'AccountApp.Patient',
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    appointment_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    prescription = models.FileField(
        upload_to='prescriptions/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_doctor_appointment_date'
            )
        ]

    def clean(self):
        super().clean()

        if not self.appointment_date:
            return

        date_changed = True

        if self.pk:
            old = Appointment.objects.filter(pk=self.pk).values_list(
                'appointment_date', flat=True
            ).first()
            date_changed = old != self.appointment_date

        if date_changed and self.appointment_date <= timezone.now():
            raise ValidationError({
                'appointment_date': "La date du rendez-vous doit être postérieure à maintenant."
            })

    def __str__(self):
        return f"{self.patient} → {self.doctor} le {self.appointment_date:%d/%m/%Y %H:%M}"
