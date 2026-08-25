# Bank MID Hosted Checkout Integration

## Required model

Use a bank- or gateway-hosted payment page. FABS creates the order and signed session, then redirects the browser. The payment provider collects PAN, expiry, CVV and any 3-D Secure authentication.

## Transaction sequence

1. FABS validates the cart and customer fields.
2. FABS creates a `pending` order and immutable order items.
3. The server signs a checkout-session request using the bank integration secret.
4. The bank returns a provider reference and hosted redirect URL.
5. The customer completes card entry and issuer authentication on the bank page.
6. The bank posts a signed webhook to `/webhooks/bank-mid`.
7. FABS verifies the signature, rejects duplicates and updates payment/order state.
8. Digital fulfilment starts only after server-side confirmation.

## Never store

- Full primary account number (PAN)
- CVV/CVC/security code
- Magnetic-stripe or equivalent authentication data
- Bank secrets in source control, templates, JavaScript or client logs

## Store for reconciliation

- FABS order reference
- Provider transaction reference
- Amount and currency
- Authorisation/result code
- Status timestamps
- Card brand and masked PAN only when returned and permitted
- Hash and unique ID of each webhook event

## Adapter work after bank selection

Update the endpoint path, request keys, authentication headers, response mapping, webhook signature algorithm and approved status values in `services/payment.py`. Do not alter the no-card-data boundary.

## Launch controls

- Sandbox approval, decline, timeout and duplicate-webhook tests
- 3-D Secure and step-up authentication tests
- Currency, decimal and maximum/minimum amount tests
- Refund and reversal API reconciliation
- Idempotency and replay protection
- Monitoring for pending/paid mismatches
- Formal merchant-acquiring and PCI scope confirmation
