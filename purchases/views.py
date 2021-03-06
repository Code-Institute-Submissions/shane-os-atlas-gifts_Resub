""" Purchases app views """
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

import stripe
import json
from cart.context import cart_items
from gifts.models import Gift
from .forms import PurchaseForm
from .models import Purchase, LineItem


@require_POST
def purchases_data_cache(request):
    try:
        payment_id = request.POST.get('client_secret').split('_secret')[0]
        print(payment_id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print(stripe.api_key)
        stripe.PaymentIntent.modify(payment_id, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'personal_info': request.POST.get('personal-info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        print("EXCEPTION: ", e)
        messages.error(request, "Error! Your payment was not processed! \
            Please try again later.")
        return HttpResponse(content=e, status=400)


def purchases(request):
    """ Display payments form page """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    total = 0
    gift_count = 0
    select_gifts = []
    print('9')

    if request.method == 'POST':
        print('10')
        cart = request.session.get('cart', {})

        data = {
            'name': request.POST['name'],
            'phone': request.POST['phone'],
            'email': request.POST['email'],
            'address_line1': request.POST['address_line1'],
            'address_line2': request.POST['address_line2'],
            'address_line3': request.POST['address_line3'],
            'town': request.POST['town'],
            'postcode': request.POST['postcode'],
            'country': request.POST['country'],
        }
        purchase_form = PurchaseForm(data)
        if purchase_form.is_valid():
            print('8')
            purchase = purchase_form.save(commit=False)
            payment_id = request.POST.get('client_secret').split('_secret')[0]
            purchase.stripe_paymentid = payment_id
            purchase.unique_cart = json.dumps(cart)
            purchase.save()
            for gift_id, quantity in cart.items():
                try:
                    gift = Gift.objects.get(id=gift_id)
                    purchase_line_item = LineItem(
                        purchase=purchase,
                        gift=gift,
                        quantity=quantity,
                    )
                    purchase_line_item.save()
                    total += gift.price * quantity
                    gift_count += quantity
                    select_gifts.append({
                        'gift_id': gift_id,
                        'quantity': quantity,
                        'gift': gift,
                    })
                except Gift.DoesNotExist:
                    messages.error(request,
                                   "We are very sorry, \
                                       but that item no longer exists.")
                    purchase.delete()
                    return redirect(reverse('view_cart'))

            request.session['personal-info'] = 'personal-info' in request.POST
            print("reaching-return")
            return redirect(reverse('purchases_success',
                                    args=[purchase.order_number]))
        else:
            print('8')
            messages.error(request, "Error! Form filled in incorrectly!")
    else:
        print('12')
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request,
                           "Your cart is currently empty! Please see our gift collection to see our exciting range!")
            return redirect(reverse('gifts'))
        # return render(request, 'purchases.html')

        cart_now = cart_items(request)
        total_now = cart_now['grandtotal']
        stripe_total_integer = round(total_now * 100)
        stripe.api_key = stripe_secret_key

        payment_intent = stripe.PaymentIntent.create(
            amount=stripe_total_integer,
            currency=settings.STRIPE_CURRENCY,
        )

        print(payment_intent)
        purchase_form = PurchaseForm()

    if not stripe_public_key:
        messages.warning(request, 'The Stripe public key is not present!')

    template = 'purchases/purchases.html'
    context = {
        'purchase_form': purchase_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': payment_intent.client_secret,
    }

    return render(request, template, context)


def purchases_success(request, order_number):
    """ Display payment confirmation page """
    personal_info = request.session.get('personal-info')
    customer_order = get_object_or_404(Purchase, order_number=order_number)
    messages.success(request, f'Your order was successful! \
                    Order Number: {order_number}.')
    if 'cart' in request.session:
        del request.session['cart']

    template = 'purchases/purchases_success.html'
    context = {
        'customer_order': customer_order,
    }

    return render(request, template, context)
