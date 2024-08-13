from app import app
from flask import render_template
from forms import SearchForm
from flask import request,flash,redirect,url_for
from helpers import search_username, search_campaign, get_campaign, get_user
import datetime as dt

@app.route('/public/profile/<int:user_id>', methods=['GET'])
def public_profile_page(user_id):
    data = get_user(user_id)
    return render_template('/public/profile.html', user=data,dt=dt)


@app.route('/public/campaign/<int:campaign_id>', methods=['GET'])
def public_campaign_page(campaign_id):
    campaign,goals_list = get_campaign(campaign_id)
    return render_template('/public/campaign.html', campaign=campaign, goals_list=goals_list, dt=dt)


@app.route('/public/find', methods=['GET','POST'])
def public_find_page():

    form = SearchForm()
    if request.method =='POST':
        if form.validate_on_submit():
            if form.choice.data == 'user':
                return redirect(url_for('public_find_page',user=form.query.data))
            if form.choice.data == 'campaign':
                return redirect(url_for('public_find_page', campaign=form.query.data))
    if request.method =='GET':

        data = []
        data_type=-1
        if 'user' in request.args:
            data = search_username(request.args['user'])
            form.query.default = request.args['user']
            form.choice.default = 'user'
            form.process()
            data_type=1
        elif 'campaign' in  request.args:
            data = search_campaign(request.args['campaign'])
            form.query.default = request.args['campaign']
            form.choice.default = 'campaign'
            form.process()
            data_type=2


        ALLOWED_ARGS = {'user', 'campaign'}
        unwanted_args = [
            arg for arg in request.args if arg not in ALLOWED_ARGS]
        if unwanted_args:
            data_type=3

        return render_template('/public/find.html', data=data, form=form, data_type=data_type, dt=dt)
