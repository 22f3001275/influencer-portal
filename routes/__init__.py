from app import app
from flask import render_template, flash, redirect, url_for,request
from forms import RegisterForm, LoginForm, CompleteRegInf, CompleteRegSponsor, MakeCampaign, MakeAdRequest, AddMoney, AdReqForm, MakeCampaignRequest, CampaignReqForm, VerifySecretKey,ProfilePicForm
from models import User, Sponsor, Influencer, Campaign, AdRequest, CampaignRequest,Notification
from db import session
from flask_login import login_user, current_user, logout_user, login_required
import re
from helpers import generate_completion_codes, checkpoints, checkpoints_inf, secret_list_generator,allowed_file
from werkzeug.utils import secure_filename
import razorpay
import datetime
import routes.notification
import routes.edit
import routes.delete
import routes.public
import routes.admin
import routes.wallet

import os

import cloudinary
import cloudinary.uploader

# Configuration
cloudinary.config(
    cloud_name="dxboktgpn",
    api_key="164964595358237",
    api_secret="-CVO4rSwDH41TrpAc7S9NkcW830",
    secure=True
)





@app.route('/switch/influencer', methods=['GET', 'POST'])
def switch_to_influencer():
    if current_user.currently_logged_in_as:  # Sponsor
        current_user.current_role = 'influencer'

    else:
        pass   # Influencer
    return redirect(url_for('dashboard_page'))


@app.route('/switch/sponsor', methods=['GET', 'POST'])
def switch_to_sponsor():
    if current_user.currently_logged_in_as:  # Sponsor
        pass

    else:
        current_user.current_role = 'sponsor'   # Influencer
    return redirect(url_for('dashboard_page'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/pay', methods=['GET', 'POST'])
@login_required
def recharge_payment_page():
    data=(request.args)
    return render_template('pay.html',data=data)


@app.route('/complete/payment', methods=['POST'])
@login_required
def complete_payment():
    client = razorpay.Client(
        auth=(
            app.config['razorpay_key_id'],
            app.config['razorpay_key_secret']
        )
    )
    print(request.form)
    payment = client.payment.fetch(request.form['razorpay_payment_id'])
    amount = payment['amount']/100
    flash(f'Payment for ₹ {amount:.2f}  Completed Successfully. ', category='success')
    current_user.add_balance(amount)
    app.logger.info('Payment LOG: %s',payment)
    return redirect(url_for('wallet_page'))

@app.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet_page():
    form = AddMoney()
    if form.validate_on_submit():
    # if True:
        client = razorpay.Client(
            auth=(
                app.config['razorpay_key_id'],
                app.config['razorpay_key_secret']
            )
        )
        data = {"amount": form.payment_amount.data*100, "currency": "INR", "receipt": "order_rcptid_11"}


        payment = client.order.create(data=data)
        return redirect(url_for('recharge_payment_page',**payment))
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error[0]}', category='danger')
    return render_template('wallet.html',form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        flash('User is already Logged in', category='info')
        return redirect(url_for('dashboard_page'))
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            name=form.name.data,
            email_address=form.email_address.data,
            password=form.password.data,
            
        )
        session.add(new_user)
        session.commit()
        login_user(new_user)
        if form.register_as.data == 'influencer':
            return redirect(url_for('complete_reg_inf'))
        elif form.register_as.data == 'sponsor':
            return redirect(url_for('complete_reg_sponsor'))

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error[0]}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        flash('User is already Logged in',category='info')
        return redirect(url_for('dashboard_page'))
    form = LoginForm()
    if form.validate_on_submit():
        entered_user = session.query(User).filter_by(
            username=form.username.data).first()

        if form.login_as.data == 'influencer' and not entered_user.is_influencer:
            flash('User is not a Influencer', category='warning')
            return redirect(url_for('login_page'))
        if form.login_as.data == 'sponsor' and not entered_user.is_sponsor:
            flash('User is not a Sponsor', category='warning')
            return redirect(url_for('login_page'))
        if form.login_as.data=='admin':
            if not entered_user.is_admin:
                flash('User is not a admin',category='danger')
                return redirect(url_for('login_page'))
        
        if entered_user and entered_user.is_password_correct(entered_password=form.password.data):
            if datetime.datetime.strptime(entered_user.banned_till,'%Y-%m-%d') > datetime.datetime.now():
                flash(f'User is Banned till {entered_user.banned_till}',category='danger')
                return redirect(url_for('login_page'))
            login_user(entered_user)
            
            current_user.current_role = form.login_as.data




            
            flash(
                f'Login SuccessFul. You are logged in as {entered_user.username}', category='success')
            session.commit()
            current_user.current_role = form.login_as.data
            # current_user.currently_logged_in_as = (form.login_as.data == 'sponsor')
            if form.login_as.data == 'admin':
                return redirect(url_for('admin_dashboard_page'))

            return redirect(url_for('dashboard_page'))
        else:
            flash(f'Username and Password do not Match', category='danger')

    if form.errors != {}:
        for error in form.errors.values():
            flash(f'{error[0]}', category='danger')
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard_page():
    profile_form=ProfilePicForm()
    if current_user.currently_logged_in_as: # Sponsor
        print('****************** Sponsor ******************')
        form = CampaignReqForm()
        

        if form.validate_on_submit():
            choice = form.choice.data
            campaign_request_id = (request.form.get('campaign_request'))
            
            
            campaign_request = session.query(CampaignRequest).get(campaign_request_id)
            campaign_end_date=datetime.datetime.strptime(campaign_request.campaign.end_date,'%Y-%m-%d')
            if campaign_end_date<datetime.datetime.now():
                flash('Campaign Expired. Contact Sponsor',category='danger')
                return redirect(url_for('dashboard_page'))

            if choice == 'accept':
                campaign_request.campaign.influencer_id = campaign_request.influencer_id
                campaign_request.campaign.status = 'Active'
                campaign_request.status = 'accepted'
                campaign_request.campaign.agreed_cost = campaign_request.payment_amount
                print(f'{campaign_request.campaign.cost}')
                additional_cost = int(
                    campaign_request.payment_amount)-int(campaign_request.campaign.cost)
                current_user.deduct_balance(
                    additional_cost)

                #! add a way to send notification to sponsor for more deduction and campaign accepted
                current_user.notify(
                    message=f'Additional ₹ {additional_cost} charged for it.', category='danger',
                    time_date=datetime.datetime.now(),

                )
                #! add a way to send notification to sponsor for more deduction and campaign accepted
                flash('Deal Successful', category='success')
                session.commit()

            if choice == 'reject':
                campaign_request.status = 'rejected'
                flash('Ad Request has Been Rejected Successfully.',
                      category='success')
                session.commit()

            if choice == 'reject_for_modification':
                campaign_request.status = 'rejected'
                flash('Ad Request has Been Rejected Successfully. Kindly fill this form to make a Fresh Ad Request',
                      category='success')

                session.commit()
                return redirect(url_for('add_ad_request', campaign=campaign_request.campaign.id, inf_username=campaign_request.influencer.user.username))
                #! code to add new campaign request

        return render_template('dashboard.html', form=form, profile_form=profile_form)

    else:   # Influencer
        print('****************** Influencer ******************')
        form = AdReqForm()
        if request.method == 'POST':
            if profile_form.submit.data and profile_form.validate_on_submit():
                file=None
                if 'profile_pic' in request.files:
                    file = request.files['profile_pic']
                    if file.filename == '':
                        # flash('No file Selected', category='warning')
                        flash('No file Selected')
                        return redirect(url_for('dashboard_page'))
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename=current_user.username + current_user.password_hash
                        # file.save(os.path.join(app.config['UPLOAD_FOLDER']), filename)

                        upload_result = cloudinary.uploader.upload(file,
                                                                public_id=filename, 
                                                                transformation="/c_fill,g_auto,w_1024,h_1024/f_auto/q_auto",)
                        # print(upload_result)
                        current_user.profile_pic = upload_result["secure_url"]
                        session.commit()
                        return redirect(url_for('dashboard_page'))
                
        if form.submit.data and form.validate_on_submit() :
            choice  = form.choice.data
            ad_request_id = (request.form.get('ad_request'))
            ad_request = session.query(AdRequest).get(ad_request_id)
            if choice == 'accept':
                campaign_id=(ad_request.campaign_id)
                campaign = session.query(Campaign).get(campaign_id)
                campaign_end_date = datetime.datetime.strptime(
                    campaign.end_date, '%Y-%m-%d')
                if campaign_end_date < datetime.datetime.now():
                    flash('Campaign Expired. Contact Sponsor', category='danger')
                    return redirect(url_for('dashboard_page'))
                campaign.influencer = int(ad_request.influencer_id)
                campaign.status='Active'
                ad_request.status='accepted'
                ad_request.campaign.agreed_cost = ad_request.payment_amount
                additional_cost = int(
                    ad_request.payment_amount)-int(ad_request.campaign.cost)
                ad_request.campaign.sponsor.user.deduct_balance(additional_cost)

                #! add a way to send notification to sponsor for more deduction and campaign accepted
                ad_request.campaign.sponsor.user.notify(
                    notification=f'Ad Request with INFLUENCER: {current_user.username} accepted. Additional ₹ {additional_cost} charged for it.',category='danger'
                    
                    )

                flash('Deal Successful',category='success')
                # session.rollback()
                session.commit()

            if choice == 'reject':
                ad_request.status = 'rejected'
                flash('Ad Request has Been Rejected Successfully.', category='success')
                session.commit()

            if choice == 'reject_for_modification':
                ad_request.status = 'rejected'
                flash('Ad Request has Been Rejected Successfully.',
                      category='success')

                session.commit()
                return redirect(url_for('add_campaign_request_page',campaign=ad_request.campaign.id))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error[0]}', category='danger')
        return render_template('dashboard.html', progress=80, form=form, profile_form=profile_form)
    




@app.route('/add/ad_request', methods=['GET', 'POST'])
@login_required
def add_ad_request():
    if current_user.is_sponsor:
        campaign_id = request.args['campaign']
        if campaign_id:
            campaign = session.query(Campaign).get(campaign_id)
            if campaign:
                if campaign.sponsor_id == current_user.sponsor.id:
                    form = MakeAdRequest(
                        inf_username=request.args.get('inf_username')
                    )
                    if form.validate_on_submit():
                        inf_user = session.query(User).filter_by(
                            username=form.inf_username.data).first()
                        new_request = AdRequest(
                            influencer_id=inf_user.influencer.id,
                            messages=form.messages.data,
                            payment_amount=form.payment_amount.data,
                            requirements=form.requirements.data,
                            campaign_id=campaign_id,
                            sponsor_id=current_user.sponsor.id

                        )
                        session.add(new_request)
                        session.commit()
                        flash(
                            f'Ad Request Successfully sent to {form.inf_username.data}',category='success')
                        
                        return redirect(url_for('view_campaign_page', campaign=campaign_id))

                    if form.errors != {}:
                        for error in form.errors.values():
                            flash(f'{error[0]}', category='danger')
                    return render_template('/add/ad_request.html', form=form)
                else:
                    flash('Not Your Campaign', category='info')
                    return redirect(url_for('dashboard_page'))

            else:
                flash('Campaign Not Found', category='info')
                return redirect(url_for('dashboard_page'))

        else:
            flash('Campaign ID Not Found', category='info')
            return redirect(url_for('dashboard_page'))
    
    else:
        flash('OOPS! Become a Sponsor to start creating Campaigns', category='danger')
        return redirect(url_for('dashboard_page'))


@app.route('/add/campaign_request', methods=['GET', 'POST'])
@login_required
def add_campaign_request_page():
    if current_user.current_role:
        flash('You are currently not logged in as a Influencer', category='success')
        return redirect(url_for('dashboard_page'))
    
    if current_user.is_influencer:
        
        campaign_id = request.args['campaign']
        if request.args['campaign']:
            campaign = session.query(Campaign).get(campaign_id)
            if campaign:
                if campaign.sponsor_id == current_user.sponsor.id:
                    form = MakeCampaignRequest()
                    if request.method == 'POST':
                        if form.validate_on_submit():
                            new_request = CampaignRequest(
                                messages=form.messages.data,
                                payment_amount=form.payment_amount.data,
                                campaign_id=campaign_id,
                                influencer_id=current_user.influencer.id
                            )
                            session.add(new_request)
                            session.commit()
                            flash(
                                f'Campaign Request Successfully sent to {campaign.sponsor.user.username}', category='success')

                            return redirect(url_for('dashboard_page'))

                        if form.errors != {}:
                            for error in form.errors.values():
                                flash(f'{error[0]}', category='danger')
                    if request.method == 'GET':
                        return render_template('/add/campaign_request.html', form=form)
                else:
                    flash('Not Your Campaign', category='info')
                    return redirect(url_for('dashboard_page'))

            else:
                flash('Campaign Not Found', category='info')
                return redirect(url_for('dashboard_page'))

        else:
            flash('Campaign ID Not Found', category='info')
            return redirect(url_for('dashboard_page'))

    else:
        flash('OOPS! Become a Sponsor to start creating Campaigns', category='danger')
        return redirect(url_for('dashboard_page'))
    



@app.route('/add/campaign', methods=['GET', 'POST'])
@login_required
def add_campaign_page():
    if not current_user.current_role:
        flash('You are currently logged in as a Influencer', category='danger')
        return redirect(url_for('dashboard_page'))
    
    if current_user.is_sponsor:
        form = MakeCampaign()
        if request.method == 'POST':
            if form.validate_on_submit():
                if current_user.wallet < form.cost.data:
                    flash(
                        'Please Recharge! You do not have enough balance to create this campaign.', category='danger')
                    return redirect(url_for('wallet_page'))
                print(form.goals.data)
                progress = generate_completion_codes(form.goals.data)
                if form.end_date.data<form.start_date.data:
                    flash('Start Date should be more than End Date',category='danger')
                    return redirect(url_for('add_campaign_page'))
                new_campaign = Campaign(
                    sponsor_id=current_user.sponsor.id,
                    name=form.name.data,
                    description=form.description.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    cost=form.cost.data,
                    visibility=(form.visibility.data == 'public'),
                    goals=form.goals.data,
                    category=form.category.data,
                    status='Incomplete',
                    secret_code=progress['completion_keys'],
                    checkpoint_weights=progress['checkpoint_weight'],
                    spare=progress['spare'],

                )
                session.add(new_campaign)
                session.commit()
                current_user.deduct_balance(form.cost.data)
                flash('Campaign Incomplete! Kindly add a Ad request',category='danger')
                return redirect(url_for('view_campaign_page', campaign=new_campaign.id))

            if form.errors != {}:
                for error in form.errors.values():
                    flash(f'{error}', category='danger')
        if request.method == 'GET':
            return render_template('/add/campaign.html', form=form)
    else:
        flash('OOPS! Become a Sponsor to start creating Campaigns', category='danger')
        return redirect(url_for('dashboard_page'))


@app.route('/view/campaign', methods=['GET', 'POST'])
@login_required
def view_campaign_page():
    form = VerifySecretKey()
    lock=False
    if not current_user.currently_logged_in_as:  #! influencer
        if current_user.is_influencer:
            campaign_id = request.args['campaign']
            if campaign_id:
                campaign = session.query(Campaign).get(campaign_id)
                
                if campaign:
                    if campaign.status == 'closed_by_sponsor':
                        flash('Campaign Closed by Sponsor. Contact Admin for money settlement if any.',category='info')
                        lock=True
                    if campaign.influencer_id == current_user.influencer.id:
                        form = VerifySecretKey()
                        goals_list = re.split(';', campaign.goals)
                        goals_list = [re.split('=', goal)[0]
                                      for goal in goals_list]
                        checkpoints_list = checkpoints_inf(
                            campaign.goals, campaign.secret_code, campaign.checkpoint_weights, campaign.spare)
                        flash(f'{checkpoints_list}',category='info')


                        if request.method == 'POST':
                            if form.validate_on_submit():
                                checkpoint_id = request.form.get('checkpoint')
                                secret_key = form.secret_key.data
                                if secret_key == checkpoints_list[int(checkpoint_id)][3] and secret_key !='Finish':
                                    if int(checkpoint_id) == -1:
                                        for checkpoint in checkpoints_list:
                                            if checkpoint[3]!='Finish':
                                                current_user.add_balance(campaign.agreed_cost * int(checkpoint[2]) /100)
                                                current_user.influencer.total_earning = current_user.influencer.total_earning + \
                                                    campaign.agreed_cost * \
                                                    int(checkpoint[2]) / 100
                                                session.commit()
                                                flash(f'Amount Credited for {checkpoint[0]}',category='success')
                                            checkpoint[3] = 'Finish'
                                        campaign.progress = 100
                                        campaign.status = 'Completed'
                                        current_user.influencer.finished_campaigns = current_user.influencer.finished_campaigns+1
                                    else:
                                        campaign.progress = campaign.progress + \
                                            int(checkpoints_list[int(checkpoint_id)][2])
                                        current_user.add_balance(
                                            campaign.agreed_cost * int(checkpoints_list[int(checkpoint_id)][2]) / 100)
                                        current_user.influencer.total_earning = current_user.influencer.total_earning + \
                                            campaign.agreed_cost * \
                                            int(checkpoints_list[int(
                                                checkpoint_id)][2]) / 100
                                        session.commit()
                                        flash(
                                            f'Amount Credited for {checkpoints_list[int(checkpoint_id)][0]}', category='success')

                                        checkpoints_list[int(
                                            checkpoint_id)][3] = 'Finish'
                                    new_secret_str = secret_list_generator(
                                            checkpoints_list)
                                    flash(f'{new_secret_str}',
                                              category='info')
                                    campaign.secret_code = new_secret_str
                                    session.commit()

                
                                else:
                                    flash('Not a correct Secret Key',category='danger')
                            
                            if form.errors != {}:
                                for error in form.errors.values():
                                    flash(f'{error[0]}', category='danger')
                            return redirect(url_for('view_campaign_page', campaign=campaign.id))
                        if request.method == 'GET':
                            return render_template('/view/campaign.html', campaign=campaign, goals_list=goals_list, progress=60, checkpoints=checkpoints_list, form=form,lock=lock)
                    else:
                        flash('Not Your Campaign', category='info')
                        return redirect(url_for('dashboard_page'))

                else:
                    flash('Campaign Not Found', category='info')
                    return redirect(url_for('dashboard_page'))

            else:
                flash('Campaign ID Not Found', category='info')
                return redirect(url_for('dashboard_page'))
        else:
            flash('OOPS! Become a Sponsor to start Campaigning', category='danger')
            return redirect(url_for('dashboard_page'))
        
        
    else: #! Sponsor
        if current_user.is_sponsor:
            campaign_id = request.args['campaign']
            if campaign_id:
                campaign = session.query(Campaign).get(campaign_id)
                if campaign:
                    if campaign.sponsor_id == current_user.sponsor.id:
                        goals_list = re.split(';', campaign.goals)
                        goals_list = [re.split('=', goal)[0]
                                    for goal in goals_list]
                        checkpoints_list = checkpoints(
                            campaign.goals, campaign.secret_code, campaign.checkpoint_weights, campaign.spare)
                        return render_template('/view/campaign.html', campaign=campaign, goals_list=goals_list, progress=60, checkpoints=checkpoints_list,form=form)
                    else:
                        flash('Not Your Campaign', category='info')
                        return redirect(url_for('dashboard_page'))

                else:
                    flash('Campaign Not Found', category='info')
                    return redirect(url_for('dashboard_page'))

            else:
                flash('Campaign ID Not Found', category='info')
                return redirect(url_for('dashboard_page'))
        else:
            flash('OOPS! Become a Sponsor to start Campaigning', category='danger')
            return redirect(url_for('dashboard_page'))
    



@app.route('/influencer/complete_registration', methods=['GET', 'POST'])
def complete_reg_inf():
    if current_user.is_influencer:
        return redirect(url_for('dashboard_page'))
    else:
        form = CompleteRegInf()
        if form.validate_on_submit():
            new_influencer = Influencer(
                influencer_id=current_user.id,
                user = current_user,
                category = form.category.data,
                niche=form.niche.data,
                reach=form.reach.data,
            )
            session.add(new_influencer)
            current_user.is_influencer=True
            current_user.currently_logged_in_as = False
            session.commit()
            return redirect(url_for('dashboard_page'))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error}', category='danger')

        return render_template('/influencer/complete_registration.html', form= form)


@app.route('/sponsor/complete_registration', methods=['GET', 'POST'])
def complete_reg_sponsor():
    if current_user.is_sponsor:
        return redirect(url_for('dashboard_page'))
    else:
        form = CompleteRegSponsor()
        if form.validate_on_submit():
            new_sponsor = Sponsor(
                sponsor_id=current_user.id,
                user=current_user,
                sponsor_type=form.sponsor_type.data,
                industry=form.industry.data
            )
            session.add(new_sponsor)
            current_user.is_sponsor = True
            current_user.currently_logged_in_as = True
            session.commit()
            return redirect(url_for('dashboard_page'))

        if form.errors != {}:
            for error in form.errors.values():
                flash(f'{error}', category='danger')
        return render_template('/sponsor/complete_registration.html', form = form)


# app.route('/recharge')
# @login_required
# def recharge_wallet_page():
#     return render_template('/add/recharge.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash('Logout Successful', category='info')
    return redirect(url_for('home_page'))
