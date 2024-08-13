from app import app
from flask import render_template, flash, redirect, url_for, request
from flask_login import  current_user,login_required
from db import session
from forms import SendNotificationForm
from models import Notification,User
import datetime
from operator import itemgetter

@app.route('/notification', methods=['GET'])
@login_required
def notification_page():
    notifications = current_user.notifications
    notifications=reversed(notifications)
    for notification in notifications:
        urgent_string = 'URGENT: 'if notification.is_urgent else ''
        flash(f'{urgent_string}{notification.message}',
              category=notification.category)
        notification.seen = True
    current_user.has_new_notifications = False
    session.commit()
    return render_template('notification.html')


@app.route('/send/notification', methods=['GET', 'POST'])
def send_notification_page():
    form = SendNotificationForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(
            username=form.username.data).first()
        new_notification = Notification(
            user_id=user.id,
            time_date=datetime.datetime.now(),
            message=form.messages.data,
            category=form.category.data,
            is_urgent=(form.category == 'danger')
        )

        #! code to notify receiver

        session.add(new_notification)
        session.commit()

    return render_template('/send/notification.html', form=form)
