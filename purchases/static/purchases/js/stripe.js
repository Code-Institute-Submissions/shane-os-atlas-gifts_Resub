// Stripe Payments
var stripePublicKey = $('#public_key_id').text().slice(1,-1);
var stripeSecretKey = $('#secret_key_id').text().slice(1,-1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style  = {
    base: {
        color: '#000',
        fontSize: '14px',
    },
    invalid: {
        color: '#cc0000',
        iconColor: '#cc0000'
    }
};

var stripeCard = elements.create('card', {style: style});
stripeCard.mount('#card-payment');

// Error Handling

stripeCard.addEventListener('change', function (event) {
    var errorResponse = document.getElementById('card-error');
    if (event.error) {
        var html = `
            <span>${event.error.message}</span>
        `;
        $(errorResponse).html(html);
    } else {
        errorResponse.textContent = '';
    }
});

// Stripe Form Submission

const stripeForm = document.getElementById('delivery-form');
console.log(stripeForm)
stripeForm.addEventListener('submit', function(e){
    e.preventDefault();
    console.log('sumbit event')
    stripeCard.update({'disabled': true});
    $('#stripe-submit').attr('disabled', true);
    $('#delivery-form').fadeToggle(100);
    $('#payment-processing-overlay').fadeToggle(100);

    var profileInfo = Boolean($('#id-personal-info').attr('checked'));
    var csrfMark = $('input[name="csrfmiddlewaretoken"]').val();
    var profileData = {
        'csrfmiddlewaretoken': csrfMark,
        'stripe_secret': stripeSecretKey,
        'profile_info': profileInfo,
    };

    var url = '/purchases/purchases_data_cache/';

    $.post(url, profileData).done(function() {
        stripe.confirmCardPayment(stripeSecretKey, {
            payment_method: {
                card: stripeCard,
                payment_details: {
                    name: $.trim(stripeForm.name.value),
                    phone: $.trim(stripeForm.phone.value),
                    email: $.trim(stripeForm.email.value),
                    payee_address: {
                        address_line1: $.trim(stripeForm.address_line1.value),
                        town: $.trim(stripeForm.town.value),
                        postcode: $.trim(stripeForm.postcode.value),
                        country: $.trim(stripeForm.country.value),
                    }
                }
            },
            delivery_details: {
                    name: $.trim(stripeForm.name.value),
                    phone: $.trim(stripeForm.phone.value),
                    recipient_address: {
                        address_line1: $.trim(stripeForm.address_line1.value),
                        town: $.trim(stripeForm.town.value),
                        postcode: $.trim(stripeForm.postcode.value),
                        country: $.trim(stripeForm.country.value),
                    }
            }
        }).then(function(result){
            if (result.error) {
                var errorResponse = document.getElementById('card-error');
                var html = `
                    <span>${result.error.message}</span>`;
                $(errorResponse).html(html);
                $('#delivery-form').fadeToggle(100);
                $('#payment-processing-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#stripe-submit').attr('disabled', false);
            } else {
                console.log(result.paymentIntent)
                if (result.paymentIntent.status === 'succeeded'){
                    stripeForm.submit();
                }
            }
        });
    }).fail(function() {
        location.reload();
    })
});