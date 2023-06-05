from django.db import models

class Doctor(models.Model):
    username = models.CharField(max_length=30,null=True,blank=True)
    first_name = models.CharField(max_length=30,null=True,blank=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Patient(models.Model):
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20,default="")
    phone = models.IntegerField()
    email = models.CharField(max_length=40)
    disease = models.CharField(max_length=40,default='')
    cured = models.BooleanField()
    doctor = models.ForeignKey('Doctor', to_field='id' , null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.firstName} {self.lastName}"

class PDates(models.Model):
    patient = models.ForeignKey('Patient', to_field='id' ,null=True, blank=True,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=False,null=True, blank=True)

    def __str__(self):
        return f"{self.patient} {self.date}"