# create signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Customer

def createCustomer(sender, instance, created, **kwargs):
    print("Customer signal triggereed", sender)
    print("UserName: ", instance)
    print("Kwargs: ", kwargs)
    if created:
        user = instance
        customer = Customer.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=user.first_name,
            id = user.id
        )
        print(customer)
        

def deleteUser(sender, instance, **kwargs):
    user = instance.user
    print(user, "got deleted deleted")
    user.delete()

# snder signal
post_save.connect(createCustomer, sender=User)
# reciever signals
post_delete.connect(deleteUser, sender=Customer)