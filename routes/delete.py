from app import app
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from db import session
from forms import EditCampaign,EditAdRequest
from models import Notification, User,Campaign,AdRequest
import datetime
from helpers import generate_completion_codes


@app.route('/close/campaign/<int:campaign_id>', methods=['GET', 'POST'])
def close_campaign_page(campaign_id):
    if current_user.currently_logged_in_as: #sponsor
        campaign=session.query(Campaign).get(campaign_id)
        if not campaign:
            flash(
                'Campaign does not exist. If it is an error contact Admin', category='danger')
            return redirect(url_for('dashboard_page'))
        if campaign.status!='Pending':
            flash(
                'Not Pending', category='danger')
            return redirect(url_for('dashboard_page'))


        if campaign.sponsor_id == current_user.sponsor.id:
            campaign.status='closed_by_sponsor'
            session.commit()
            return redirect(url_for('view_campaign_page', campaign=campaign.id))

        else:
            flash('You are not the creator of Campaign. If it is an error contact Admin',category='danger')
            return redirect(url_for('dashboard_page'))

    else:
        flash('Switch to Sponsor Mode to edit a Campaign', category='info')
        return redirect(url_for('dashboard_page'))
    

@app.route('/close/ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def close_ad_request_page(ad_request_id):
    if current_user.currently_logged_in_as:  # sponsor
        ad_request = session.query(AdRequest).get(ad_request_id)
        if ad_request.status=='accepted':
            flash(
                'OOPS! Can not edit this Ad Request.Ad Request already accepted. If it is an error contact Admin', category='danger')
            return redirect(url_for('view_campaign_page',campaign=ad_request.campaign.id))
        if not ad_request:
            flash(
                'Ad Request does not exist. If it is an error contact Admin', category='danger')
            return redirect(url_for('dashboard_page'))

        if ad_request.status != 'Pending':
            flash('Not Pending', category='danger')
            return redirect(url_for('view_campaign_page', campaign=ad_request.campaign.id))
        
        if ad_request.sponsor_id == current_user.sponsor.id:
            ad_request.status = 'closed_by_sponsor'
            return redirect(url_for('view_campaign_page', campaign=ad_request.campaign.id))
        

        else:
            flash(
                'You are not the creator of Campaign. If it is an error contact Admin', category='danger')
            return redirect(url_for('dashboard_page'))

    else:
        flash('Switch to Sponsor Mode to edit a Campaign', category='info')
        return redirect(url_for('dashboard_page'))
