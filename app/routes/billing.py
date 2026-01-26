from datetime import datetime, timedelta
import os
from uuid import uuid4

from flask import Blueprint, current_app, redirect, request, url_for, flash, render_template
from flask_login import login_required, current_user
from flask_babel import _

from app.extensions import db
from app.models.payment import Payment
from app.models.user import User
from app.services.fondy import create_checkout_url, verify_signature


billing_bp = Blueprint("billing", __name__)

APPROVED_STATUSES = {"approved", "success", "successful", "paid"}
FAILED_STATUSES = {"declined", "expired", "reversed", "failure", "failed", "rejected"}


def _is_fake_enabled() -> bool:
    provider = (current_app.config.get("BILLING_PROVIDER") or "").lower()
    if provider == "fake":
        return True
    if current_app.debug:
        return True
    return (os.environ.get("FLASK_ENV") or "").lower() == "development"


def _extract_fondy_payload():
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        if isinstance(data.get("response"), dict):
            return data["response"]
        if isinstance(data.get("request"), dict):
            return data["request"]
        if data:
            return data
    if request.form:
        return request.form.to_dict(flat=True)
    return {}


@billing_bp.post("/billing/fondy/create")
@login_required
def create_fondy_payment():
    merchant_id = current_app.config.get("FONDY_MERCHANT_ID")
    secret_key = current_app.config.get("FONDY_SECRET_KEY")
    if not merchant_id or not secret_key:
        flash(_("Payment is not configured"), "danger")
        return redirect(url_for("billing.billing_overview"))

    merchant_id = str(merchant_id).strip()

    if current_user.is_pro and current_user.pro_until and current_user.pro_until > datetime.utcnow():
        flash(_("You already have an active Pro subscription"), "info")
        return redirect(url_for("billing.billing_overview"))

    amount = current_app.config.get("PRO_AMOUNT")
    currency = current_app.config.get("PRO_CURRENCY")
    duration_days = current_app.config.get("PRO_DURATION_DAYS")

    order_id = f"pro_{uuid4().hex}"
    order_desc = _("SkillTracker Pro ({days} days)").format(days=duration_days)

    payment = Payment(
        user_id=current_user.id,
        order_id=order_id,
        amount=amount,
        currency=currency,
        status="pending",
        provider="fondy",
    )
    db.session.add(payment)
    db.session.commit()

    response_url = url_for("billing.billing_success", order_id=order_id, _external=True)
    callback_url = url_for("billing.fondy_callback", _external=True)

    payload = {
        "merchant_id": merchant_id,
        "order_id": order_id,
        "order_desc": order_desc,
        "amount": amount,
        "currency": currency,
        "sender_email": current_user.email,
        "response_url": response_url,
        "server_callback_url": callback_url,
    }

    try:
        checkout_url = create_checkout_url(payload)
    except Exception as exc:
        payment.status = "failed"
        db.session.commit()
        flash(_("Unable to start payment: {error}").format(error=str(exc)), "danger")
        return redirect(url_for("billing.billing_overview"))

    return redirect(checkout_url)


@billing_bp.post("/billing/fondy/callback")
def fondy_callback():
    payload = _extract_fondy_payload()
    secret_key = current_app.config.get("FONDY_SECRET_KEY")
    if not secret_key:
        return "missing secret", 500

    if not verify_signature(payload, secret_key):
        return "invalid signature", 400

    order_id = payload.get("order_id")
    if not order_id:
        return "missing order_id", 400

    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        return "payment not found", 404

    status = (payload.get("order_status") or "").lower()
    if payment.status == "paid":
        return "ok", 200

    if status in APPROVED_STATUSES:
        payment.status = "paid"
        try:
            payment.amount = int(payload.get("amount", payment.amount) or payment.amount)
        except (TypeError, ValueError):
            pass
        payment.currency = payload.get("currency", payment.currency)

        user = db.session.get(User, payment.user_id)
        if user:
            user.is_pro = True
            duration_days = current_app.config.get("PRO_DURATION_DAYS")
            user.pro_until = datetime.utcnow() + timedelta(days=duration_days)
        db.session.commit()
        return "ok", 200

    if status in FAILED_STATUSES or status:
        payment.status = "failed"
        db.session.commit()

    return "ok", 200


@billing_bp.route("/billing/success", methods=["GET", "POST"])
def billing_success():
    payload = _extract_fondy_payload()
    status = (payload.get("order_status") or "").lower()
    order_id = payload.get("order_id") or request.args.get("order_id")

    if status and status not in APPROVED_STATUSES:
        flash(_("Payment failed"), "danger")
        return redirect(url_for("billing.billing_fail"))

    if status in APPROVED_STATUSES:
        flash(_("Payment successful, Pro activated"), "success")

    if not status and order_id:
        payment = Payment.query.filter_by(order_id=order_id).first()
        if payment and payment.status == "paid":
            flash(_("Payment successful, Pro activated"), "success")
        elif payment and payment.status == "failed":
            flash(_("Payment failed"), "danger")
            return redirect(url_for("billing.billing_fail"))

    return render_template("billing_success.html", order_id=order_id)


@billing_bp.route("/billing/fail", methods=["GET", "POST"])
def billing_fail():
    flash(_("Payment failed"), "danger")
    return render_template("billing_fail.html")


@billing_bp.post("/billing/fake/activate")
@login_required
def fake_activate():
    if not _is_fake_enabled():
        flash(_("Payment is not configured"), "danger")
        return redirect(url_for("billing.billing_overview"))

    amount = current_app.config.get("PRO_AMOUNT")
    currency = current_app.config.get("PRO_CURRENCY")
    duration_days = current_app.config.get("PRO_DURATION_DAYS")
    order_id = f"fake_{uuid4().hex}"

    payment = Payment(
        user_id=current_user.id,
        order_id=order_id,
        amount=amount,
        currency=currency,
        status="paid",
        provider="fake",
    )
    db.session.add(payment)

    current_user.is_pro = True
    current_user.pro_until = datetime.utcnow() + timedelta(days=duration_days)
    db.session.commit()

    flash(_("Payment successful, Pro activated"), "success")
    return redirect(url_for("billing.billing_overview"))


@billing_bp.get("/settings/billing")
@login_required
def billing_overview():
    amount = current_app.config.get("PRO_AMOUNT")
    currency = current_app.config.get("PRO_CURRENCY")
    duration_days = current_app.config.get("PRO_DURATION_DAYS")
    provider = (current_app.config.get("BILLING_PROVIDER") or "fake").lower()
    return render_template(
        "billing.html",
        amount=amount,
        currency=currency,
        duration_days=duration_days,
        provider=provider,
        fake_enabled=_is_fake_enabled(),
    )


@billing_bp.get("/billing")
@login_required
def billing_redirect():
    return redirect(url_for("billing.billing_overview"))
