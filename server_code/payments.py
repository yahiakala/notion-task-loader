"""Payments functions with LemonSqueezy API."""
import anvil.server
import anvil.http
import anvil.secrets
import anvil.users
import json
import hmac
import hashlib
from anvil.tables import app_tables

from anvil_squared.helpers import print_timestamp

prod_url = 'app.chatbeaver.ca'


if anvil.server.get_app_origin() and prod_url in anvil.server.get_app_origin():
    product_id = ''
    lemon_signing = 'LEMON_SIGNING'
    lemon_api = 'LEMON_API'
else:
    product_id = '197208'
    lemon_signing = 'LEMON_SIGNING_TEST'
    lemon_api = 'LEMON_API_TEST'


@anvil.server.http_endpoint('/lemon_webhook', methods=['POST'])
def lemon_webhook():
    """Catch-all endpoint for lemonsqueezy webhooks."""
    print_timestamp("lemon_webhook")
    signature = anvil.server.request.headers.get('x-signature')

    if not signature:
        return anvil.server.HttpResponse(body="Missing signature", status=400)

    event = anvil.server.request.headers.get('x-event-name')
    
    secret = anvil.secrets.get_secret(lemon_signing)
    
    payload = anvil.server.request.body.get_bytes()
    
    # Compute the HMAC digest
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    
    # Compare the computed digest with the provided signature
    if not hmac.compare_digest(digest, signature):
        # Return a 403 Forbidden status code if the signature is invalid
        return anvil.server.HttpResponse(body="Invalid signature", status=403)

    payload_dict = json.loads(payload.decode('utf-8'))
    # print(event)
    print(anvil.server.request.body)
    print(payload)

    event_name = payload_dict['meta']['event_name']
    print(event_name)

    user_dict = {}

    if event_name == 'subscription_created' or event_name == 'subscription_updated':
        # Returns subscription object.
        user_dict['subscription_id'] = payload_dict['data']['id']
        user_dict['store_id'] = payload_dict['data']['attributes']['store_id']
        user_dict['customer_id'] = payload_dict['data']['attributes']['customer_id']
        user_dict['product_id'] = payload_dict['data']['attributes']['product_id']
        user_dict['variant_id'] = payload_dict['data']['attributes']['variant_id']
        user_dict['variant_name'] = payload_dict['data']['attributes']['variant_name']
        user_dict['user_email'] = payload_dict['data']['attributes']['user_email']
        # only care about 'active' and 'expired' unless it is paused
        user_dict['status'] = payload_dict['data']['attributes']['status']
        user_dict['pause'] = payload_dict['data']['attributes']['pause']
        user_dict['cancelled'] = payload_dict['data']['attributes']['cancelled']

        print_timestamp(user_dict['product_id'])
        if str(user_dict['product_id']) == product_id:
            update_user_permissions(user_dict)
    elif event_name == 'subscription_payment_success':
        # Returns a subscription invoice object
        user_dict['store_id'] = payload_dict['data']['attributes']['store_id']
        user_dict['subscription_id'] = payload_dict['data']['attributes']['subscription_id']
        user_dict['user_email'] = payload_dict['data']['attributes']['user_email']
        user_dict['customer_id'] = payload_dict['data']['attributes']['customer_id']
    elif event == 'subscription_updated':
        pass

    # except Exception as e:
        # return anvil.server.HttpResponse(f"Error processing request: {str(e)}", status=500)
    return anvil.server.HttpResponse(body="Signature verified", status=200)


def update_user_permissions(user_dict):
    """Update the user permissions."""
    print_timestamp(f"update_user_permissions: email: {user_dict['user_email']}, variant_name: {user_dict['variant_name']}")
    user = app_tables.users.get(customer_id=str(user_dict['customer_id']))
    if not user:
        user = app_tables.users.get(email=user_dict['user_email'])
    role = app_tables.roles.get(name=user_dict['variant_name'])
    maprow = app_tables.usertenant.get(user=user)

    if user:
        if not maprow:
            maprow = app_tables.usertenant.add_row(user=user)
        maprow['customer_id'] = str(user_dict['customer_id'])
        if not role:
            role = app_tables.roles.add_row(name=user_dict['variant_name'])

        if user_dict['status'] == 'expired':  # Remove role
            maprow['roles'] = [i for i in maprow['roles'] if i != role]
        else:  # Add role or no change
            if maprow['roles']:
                if role not in maprow['roles']:
                    maprow['roles'] += role
            else:
                maprow['roles'] = [role]


@anvil.server.callable(require_user=True)
def get_customer_portal():
    """Get the URL for the customer portal."""
    from anvil_squared.lemons import get_customer
    user = anvil.users.get_user(allow_remembered=True)
    usertenant = app_tables.usertenant.get(user=user)
    if not usertenant:
        return ''
    elif not usertenant['customer_id']:
        return ''
    cust_portal, _ = get_customer(
        api_key=anvil.secrets.get_secret(lemon_api),
        customer_id=usertenant['customer_id']
    )
    return cust_portal