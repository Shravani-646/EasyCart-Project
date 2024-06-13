from store.signals import order_created
from django.dispatch import receiver
@receiver(signal=order_created)
def on_order_created(sender,**kwargs):
    if kwargs["order"]:
        print("Order created")