from db import session
from models import User,Campaign
import re


def search_username(input):
    users = session.query(User).filter(User.username.like('%'+input+'%'))
    users=users.order_by(User.username).all()
    return users


def search_campaign(input, isAdmin=False):


    campaigns_query = session.query(Campaign).filter(
        Campaign.name.like('%'+input+'%'))

    if not isAdmin:
        campaigns_query = campaigns_query.filter(Campaign.visibility == True)
    campaigns = campaigns_query.order_by(Campaign.name).all()

    campaigns_query = session.query(Campaign).filter(
        Campaign.description.like('%'+input+'%'))
    if not isAdmin:
        campaigns_query = campaigns_query.filter(Campaign.visibility == True)
    campaigns.extend(campaigns_query.order_by(Campaign.name).all())

    campaigns_query = session.query(Campaign).filter(
        Campaign.category.like('%'+input+'%'))
    if not isAdmin:
        campaigns_query = campaigns_query.filter(Campaign.visibility == True)
    campaigns.extend(campaigns_query.order_by(Campaign.name).all())
    campaigns=list(set(campaigns))
    return campaigns

def get_campaign(campaign_id):
    campaign = session.query(Campaign).get(campaign_id)
    goals_list = re.split(';', campaign.goals)
    goals_list = [re.split('=', goal)[0]
                  for goal in goals_list]
    return campaign,goals_list

def get_user(user_id):
    user = session.query(User).get(user_id)
    return user
