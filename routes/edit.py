from app import app
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from db import session
from forms import EditCampaign,EditAdRequest
from models import Notification, User,Campaign,AdRequest
import datetime
from helpers import generate_completion_codes


@app.route('/edit/campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign_page(campaign_id):
    if current_user.currently_logged_in_as: #sponsor
        campaign=session.query(Campaign).get(campaign_id)
        if not campaign:
            flash(
                'Campaign does not exist. If it is an error contact Admin', category='danger')
            return redirect(url_for('dashboard_page'))


        if campaign.sponsor_id == current_user.sponsor.id:
            form = EditCampaign(
                name=campaign.name,
                description=campaign.description,
                start_date=datetime.datetime.strptime(campaign.start_date,'%Y-%m-%d'),
                end_date=datetime.datetime.strptime(campaign.end_date,'%Y-%m-%d'),
                cost=campaign.cost,
                visibility=campaign.visibility,
                goals=campaign.goals,
                category=campaign.category,
            )
            if form.validate_on_submit():
                if form.end_date.data < form.start_date.data:
                    flash('Start Date should be more than End Date',
                          category='danger')
                    return redirect(url_for('edit_campaign_page',campaign_id=campaign_id))
                addtional_cost = form.cost.data-int(campaign.cost)
                if current_user.wallet < addtional_cost:
                    flash(
                        'Please Recharge! You do not have enough balance to create this campaign.', category='danger')
                    return redirect(url_for('wallet_page'))
                print(form.goals.data)
                progress = generate_completion_codes(form.goals.data)
                
                campaign.sponsor_id = current_user.sponsor.id
                campaign.name = form.name.data
                campaign.description = form.description.data
                campaign.start_date = form.start_date.data
                campaign.end_date = form.end_date.data
                campaign.cost = form.cost.data
                campaign.visibility = (form.visibility.data == 'public')
                campaign.goals = form.goals.data
                campaign.category = form.category.data
                campaign.status = 'Incomplete'
                campaign.secret_code = progress['completion_keys']
                campaign.checkpoint_weights = progress['checkpoint_weight']
                campaign.spare = progress['spare']
                campaign.progress=0
                session.commit()
                current_user.deduct_balance(addtional_cost)
                return redirect(url_for('view_campaign_page', campaign=campaign_id))

            if form.errors != {}:
                for error in form.errors.values():
                    flash(f'{error}', category='danger')
            return render_template('/edit/campaign.html',form=form)
            
        else:
            flash('You are not the creator of Campaign. If it is an error contact Admin',category='danger')
            return redirect(url_for('dashboard_page'))

    else:
        flash('Switch to Sponsor Mode to edit a Campaign', category='info')
        return redirect(url_for('dashboard_page'))
    

@app.route('/edit/ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def edit_ad_request_page(ad_request_id):
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

        if ad_request.sponsor_id == current_user.sponsor.id:
            form = EditAdRequest(
                inf_username=ad_request.influencer.user.username,
                messages=ad_request.messages,
                payment_amount=ad_request.payment_amount,
                requirements=ad_request.requirements
            )
            if form.validate_on_submit():
                
                inf_user = session.query(User).filter_by(
                    username=form.inf_username.data).first()
                ad_request.influencer_id = inf_user.influencer.id
                ad_request.messages = form.messages.data
                ad_request.payment_amount = int(form.payment_amount.data)
                ad_request.requirements = form.requirements.data
                session.commit()
                flash(
                        f'Ad Request Successfully sent to {form.inf_username.data}', category='success')

                return redirect(url_for('view_campaign_page', campaign=ad_request.campaign.id))


            if form.errors != {}:
                for error in form.errors.values():
                    flash(f'{error}', category='danger')
            return render_template('/edit/ad_request.html', form=form)

        else:
            flash(
                'You are not the creator of Campaign. If it is an error contact Admin', category='danger')
            return redirect(url_for('dashboard_page'))

    else:
        flash('Switch to Sponsor Mode to edit a Campaign', category='info')
        return redirect(url_for('dashboard_page'))
